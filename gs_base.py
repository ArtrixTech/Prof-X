from scholarly import scholarly

search_query = scholarly.search_author('Danyang Xie')
author = scholarly.fill(next(search_query))
print(author)