import os
import sys
from pprint import pprint as pp
import SoftLayer

def getOrderItemsDict(client, pkgId, location=None, displayFiltered=False):
    '''Get all of the item price objects for the given pkg, keyed by the keyName, with the id as the value,
    and organize these keyName/id pairs by category.  The issue here is that keyName is the same between accounts,
    the id is not.  But it is the id that we need to pass into the order. 
    If location==None, return only the location independent price objects.
    If location==*, return both the location independent and all of the location specific price objects, with the location short name appended to the item keyName.
    If location!=None, return the location specific price objects for that location (or location independent if there is no location-specific one).'''
    # We intentionally are not catching exceptions so they will be raised all the way to the top.
    # Build a dict of each category id and what its categoryCode is.  This is only used to build the item dict below.
    # http://sldn.softlayer.com/reference/services/SoftLayer_Product_Package/getConfiguration
    categories = client['Product_Package'].getConfiguration(id=pkgId, mask='isRequired, itemCategory.id, itemCategory.name, itemCategory.categoryCode')
    cats = {}
    for cat in categories:
        catid = cat['itemCategory']['id']
        cats[catid] = {'code':cat['itemCategory']['categoryCode'], 'name':cat['itemCategory']['name'], 'isRequired':(cat['isRequired'] == 1)}

    # Go thru the items for this pkg and put the key/id pair in the correct category
    # Note: the keys are only unique within a category, not between categories
    mask = 'mask[id,recurringFee,hourlyRecurringFee,locationGroupId,capacityRestrictionMaximum,item[id,description,keyName],categories[id],pricingLocationGroup[name,locations[name]]]'
    # http://sldn.softlayer.com/reference/services/SoftLayer_Product_Package/getItemPrices
    itemPriceList = client['Product_Package'].getItemPrices(id=pkgId, mask=mask)

    # Process the item prices:  choose the item prices for this location (defaulting to location-independent item prices), eliminate duplicates,
    # handle duplicates with different capacity values, and flag duplicate item prices that have different prices.
    result = {}          # this is what we will return, a 2 level dict: 1st key is categoryCode, 2nd key is item keyName, value is item id
    for itemP in itemPriceList:
        if 'categories' not in itemP:  continue
        item = itemP['item']
        itemId = item['id']
        itemDesc = item['description']
        itemKeyName = item['keyName']       # need to reset this each iteration of the loop
        # simplify the check for location-specific item price
        if 'locationGroupId' in itemP and itemP['locationGroupId'] and 'pricingLocationGroup' in itemP and 'locations' in itemP['pricingLocationGroup'] and itemP['pricingLocationGroup']['locations']:
            itemLocations = itemP['pricingLocationGroup']['locations']
        else:
            itemLocations = None
        if location and location!='*':
            # We want the item prices that apply to this location specifically, or are location-independent.
            # Ignore this item if it has a location but the location list does not include the one we want
            if itemLocations and not isLocInGroup(location, itemLocations): continue
        elif not location:
            # We want only location independent item prices
            if itemLocations:  continue
        # elif location=='*':  pass   # we want all location independent and specific item prices, so nothing to eliminate at this point
        # pkg 200 is for bare metal preset hourly configs, so only want item prices that are valid for hourly
        if pkgId==200 and 'hourlyRecurringFee' not in itemP:  continue
        if 'capacityRestrictionMaximum' in itemP:
            # we will probably find multiple item price objects with the same keyName, so append the capacityRestrictionMaximum to make them unique
            itemKeyName += '_Max_'+str(itemP['capacityRestrictionMaximum'])
        if location=='*' and itemLocations:
            # We will find multiple item price objects with the same keyName, so append the location names to make them unique
            itemKeyName += concatLocations(itemLocations)
        if 'recurringFee' in itemP:
            itemFee = itemP['recurringFee']
        else:
            itemFee = '0'
        if 'hourlyRecurringFee' in itemP:
            itemHourlyFee = itemP['hourlyRecurringFee']
        else:
            itemHourlyFee = None
        # Go thru this item's supported categories
        for itemPriceCat in itemP['categories']:
            itemCatId = itemPriceCat['id']
            # We correlate the categories and items by the category id
            if itemCatId not in cats:  continue         # this cat of this item price does not apply to this pkg
            # This item supports a category in this package, so add it to the structure under this category
            categoryCode = cats[itemCatId]['code']
            # If we haven't yet added an entry for this categoryCode, create it now
            if categoryCode not in result:  result[categoryCode] = {'catName':cats[itemCatId]['name'], 'isRequired':cats[itemCatId]['isRequired'], 'items':{}}
            entry = {'id':itemId, 'priceId':itemP['id'], 'description':itemDesc, 'fee':itemFee, 'locationGroupId':itemP['locationGroupId']}
            if 'pricingLocationGroup' in itemP:  entry['pricingLocationGroup'] = itemP['pricingLocationGroup']
            if itemHourlyFee:  entry['hourlyFee'] = itemHourlyFee
            if 'capacityRestrictionMaximum' in itemP:  entry['capacityRestrictionMaximum'] = itemP['capacityRestrictionMaximum']
            if location and location!='*' and not itemLocations and itemKeyName in result[categoryCode]['items'] and result[categoryCode]['items'][itemKeyName]['locationGroupId']:
                pass        # the item price is not location-specific, so do not overwrite a location-specific item that is already there
            elif location and location!='*' and itemLocations and itemKeyName in result[categoryCode]['items'] and not result[categoryCode]['items'][itemKeyName]['locationGroupId']:
                # the item price is location-specific, and the existing entry is not location-specific, so overwrite it
                result[categoryCode]['items'][itemKeyName] = entry
                # also get rid of other non-location-specific entries that were added as dups
                keyName = itemKeyName+'-dup'
                for i in range(7):
                    if keyName not in result[categoryCode]['items']:  break
                    if not result[categoryCode]['items'][keyName]['locationGroupId']:
                        # this is not location-specific, so delete it
                        if displayFiltered:  print 'Filtering out duplicate item price '+keyName+' in category '+categoryCode+' that does not matter because it is overridden by a location-specific item price: '+str(result[categoryCode]['items'][keyName])
                        del result[categoryCode]['items'][keyName]
                    keyName = keyName+'-dup'

            else:
                # This is not one of the special cases above, so make the key unique (if necessary) and put the entry in
                keyName = itemKeyName
                for i in range(7):
                    if keyName in result[categoryCode]['items']:
                        # If this is a duplicate entry in all of the important properties, we can discard it
                        if isEquivalentItemPrice(entry, result[categoryCode]['items'][keyName]):
                            if displayFiltered:  print 'Filtering out duplicate item price in '+keyName+' in category '+categoryCode+' because it is equivalent to an existing one: '+str(entry)
                            break
                        # Otherwise this is not an exact duplicate, but has the same key, so modify the key a little and try again
                        keyName = keyName+'-dup'
                    else:
                        # we do not already have an entry with that key so add it
                        result[categoryCode]['items'][keyName] = entry
                        break
    return result


# These 3 functions are used by getOrderItemsDict()
def isLocInGroup(loc, locations):
    '''Return True if the specified short location name is in the list of locations given (that usually comes from a SL Location_Group).
    Locations is an list of dicts, each with a key called "name".'''
    for l in locations:
        if l['name'] == loc:  return True
    return False


def concatLocations(locations):
    '''Return a string that is a concatenation of all of the short location names in the list of locations specified.'''
    locStr = ''
    for l in locations:
        locStr += '-'+l['name']
    return locStr


def isEquivalentItemPrice(entry1, entry2):
    '''Compare the important values in the 2 item price entries to determine if they are equivalent.'''
    if entry1['description'] != entry2['description']:  return False
    if entry1['fee'] != entry2['fee']:  return False
    if entry1['id'] != entry2['id']:  return False
    if 'hourlyFee' in entry1:
        if 'hourlyFee' in entry2 and entry1['hourlyFee'] != entry2['hourlyFee']:  return False
    elif 'hourlyFee' not in entry2:  return False
    else:       # hourlyFee not in entry1
        if 'hourlyFee' in entry2:  return False
    return True     # all tests passed


def getItemPriceId(items, catCode, itemKey):
    '''Return the item price id for this category and item key.  Use this function to pull an item out of
    the structure built by getOrderItemsDict(), using the category and item keyName you want.'''
    # note: the KeyError exception will bubble up to the calling function
    cat = items[catCode]
    item = cat['items']
    return item[itemKey]['priceId']


def getLocationId(client, name):
    '''Return the id of the datacenter specified by its short name.'''
    filt = {'name': {'operation': name}}
    locations = client['Location'].getDataCenters(mask='id, name', filter=filt)
    if len(locations) != 1:
        print 'Could not find exactly 1 datacenter named '+name
        sys.exit(2)
    return locations[0]['id']

