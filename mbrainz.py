import musicbrainzngs as mbngs
import json
import urllib

class mb():
    def __init__(self):
        mbngs.set_useragent('record-shelf-app', 1, 'biast@oregonstate.edu')
        self.result = None
        self.url = ""
        self.returnData = {}
        self.filename = ""
        self.releaseGroupID = ""
        self.releaseResult = None
        return

    # Data needs to be given as a dict containing the search query, indexed by 'artist' and 'title'
    def get_data(self, data):
        self.result = mbngs.search_release_groups(('%s' % data['Title']), artist=('%s'%data['Artist']), primarytype='album')

        
        x = 0
        while True:
            topResult = self.result['release-group-list'][x]
            topID = topResult['id']
            try:
                pics = mbngs.get_release_group_image_list(topID)
                self.releaseGroupID = topID
                break
            except:
                x += 1
                
        self.url = pics['images'][0]['image']

        self.filename = self.url.split('/')[-1]
        
        # Used for testing / devlopment. Save the cover art to a local directory.
        # urllib.urlretrieve(self.url, self.filename)
        
        self.returnData['Art'] = self.url
        self.releaseResult = mbngs.get_release_group_by_id(self.releaseGroupID)

        
        self.returnData['Date'] = self.releaseResult['release-group']['first-release-date']
        
        print self.returnData
        
        return self.returnData

        
    # Used for testing and development. Save a json blob into a txt file so that it can be parsed by an external utility and examined
    def print_to_file(self, filename, data):
        print filename
        with open(filename, 'w+') as f:
            json.dump(data, f)
            f.close()
        return


# brainz = mb()
# brainz.get_data({'artist': 'third eye blind', 'title': 'third eye blind'})