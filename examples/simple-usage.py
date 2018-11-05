
from amazonproduct.simple import *

init("XXXX", "xxx", "de", "redtoad-21")
root = ItemSearch(Keywords="python", SearchIndex="Books", ResponseGroup="Large", ItemPage=1, TruncateReviewsAt=0)
nspace = root.nsmap.get(None, "")

#import lxml.etree
#print(lxml.etree.tostring(root, pretty_print=True).decode("utf-8"))

for item in root.xpath("//aws:Items/aws:Item", namespaces={"aws": nspace}):
    print("# {item.ASIN} {item.ItemAttributes.Author}: {item.ItemAttributes.Title}".format(item=item))
    print("![]({item.LargeImage.URL})".format(item=item))
    reviews = item.xpath("aws:EditorialReviews/aws:EditorialReview", namespaces={"aws": nspace})
    for review in reviews:
        print("## {review.Source}".format(review=review))
        print(review.Content)