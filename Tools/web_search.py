from ddgs import DDGS
from json import JSONEncoder
def web_search(topic,k):

    with DDGS() as ddgs:

        results = ddgs.text(
            topic,
            max_results=k
        )

    return results


#print(web_search("python", 5))
