import musicbrainzngs as mb
import json

def print_to_file(filename, data):
    print filename
    with open(filename, 'w+') as f:
        json.dump(data, f)
        f.close()
    return

mb.set_useragent('record-shelf-app', 1, 'biast@oregonstate.edu')

artist = 'pile'

result = mb.search_artists(artist)
topResult = result['artist-list'][1]
topID = topResult['id']

artistData = mb.get_artist_by_id(topID, includes=['release-groups'], release_type=['album'])

theList = artistData['artist']['release-group-list']
print len(theList)
listCounter = 0
counter = 0
indexTracker = []
for x in range(0, len(theList)):
    if theList[x]['type'] != "Album":
        counter += 1
        print counter
        indexTracker.append(x)
        print "bottom %s" % len(theList)
             
print indexTracker
 
for x in range(len(indexTracker)-1, -1, -1):
    y = indexTracker[x]
    theList.pop(y)
 
artistData['artist']['release-group-list'] = theList

print_to_file(('%s.txt' % artist), artistData)
