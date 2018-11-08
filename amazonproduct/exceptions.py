
class AWSError(Exception):

    """
    Generic AWS error message.
    """


class UnknownLocale(AWSError):
    """
    Raised when unknown locale is specified.
    """

class InternalError(AWSError):
    """
    Amazon encountered an internal error. Please try again.
    """

class InvalidClientTokenId(AWSError):
    """
    The AWS Access Key Id you provided does not exist in Amazon's records.
    """

class MissingClientTokenId(AWSError):
    """
    Request must contain AWSAccessKeyId or X.509 certificate.
    """

class InvalidSignature(AWSError):
    """
    The AWS Secret key you provided is invalid.
    """

class InvalidAccount(AWSError):
    """
    Your account has no access to the product API.
    """

class MissingParameters(AWSError):
    """
    Your request is missing required parameters. Required parameters include
    XXX.
    """

class ParameterOutOfRange(AWSError):
    """
    The value you specified for XXX is invalid.
    """

class InvalidSearchIndex(AWSError):
    """
    The value specified for SearchIndex is invalid. Valid values include:

    All, Apparel, Automotive, Baby, Beauty, Blended, Books, Classical, DVD,
    Electronics, ForeignBooks, HealthPersonalCare, HomeGarden, HomeImprovement,
    Jewelry, Kitchen, Magazines, MP3Downloads, Music, MusicTracks,
    OfficeProducts, OutdoorLiving, PCHardware, Photo, Shoes, Software,
    SoftwareVideoGames, SportingGoods, Tools, Toys, VHS, Video, VideoGames,
    Watches
    """

class InvalidResponseGroup(AWSError):
    """
    The specified ResponseGroup parameter is invalid. Valid response groups for
    ItemLookup requests include:

    Accessories, AlternateVersions, BrowseNodes, Collections, EditorialReview,
    Images, ItemAttributes, ItemIds, Large, ListmaniaLists, Medium,
    MerchantItemAttributes, OfferFull, OfferListings, OfferSummary, Offers,
    PromotionDetails, PromotionSummary, PromotionalTag, RelatedItems, Request,
    Reviews, SalesRank, SearchBins, SearchInside, ShippingCharges,
    Similarities, Small, Subjects, Tags, TagsSummary, Tracks, VariationImages,
    VariationMatrix, VariationMinimum, VariationOffers, VariationSummary,
    Variations.
    """

class InvalidParameterValue(AWSError):
    """
    The specified ItemId parameter is invalid. Please change this value and
    retry your request.
    """

class InvalidListType(AWSError):
    """
    The value you specified for ListType is invalid. Valid values include:
    BabyRegistry, Listmania, WeddingRegistry, WishList.
    """

class NoSimilarityForASIN(AWSError):
    """
    When you specify multiple items, it is possible for there to be no
    intersection of similar items.
    """

class NoExactMatchesFound(AWSError):
    """
    We did not find any matches for your request.
    """

class TooManyRequests(AWSError):
    """
    You are submitting requests too quickly and your requests are being
    throttled. If this is the case, you need to slow your request rate to one
    request per second.
    """

class NotEnoughParameters(AWSError):
    """
    Your request should have at least one parameter which you did not submit.
    """

class InvalidParameterCombination(AWSError):
    """
    Your request contained a restricted parameter combination.
    """

class DeprecatedOperation(AWSError):
    """
    The specified feature (operation) is deprecated.
    """

class InvalidOperation(AWSError):
    """
    The specified feature (operation) is invalid.
    """

class InvalidCartItem(AWSError):
    """
    The item you specified, ???, is not eligible to be added to the cart. Check
    the item's availability to make sure it is available.
    """

class ItemAlreadyInCart(AWSError):
    """
    The item you specified, ???, is already in your cart.
    
    .. deprecated:: 0.2.6
    """

class CartInfoMismatch(AWSError):
    """
    Your request contains an invalid AssociateTag, CartId and HMAC combination.
    Please verify the AssociateTag, CartId, HMAC and retry.

    Remember that all Cart operations must pass in the CartId and HMAC that were
    returned to you during the CartCreate operation.
    """

class InvalidCartId(AWSError):
    """
    Your request contains an invalid value for CartId. Please check your CartId
    and retry your request.
    """

class AccountLimitExceeded(AWSError):
    """
    Account limit of 2000 requests per hour exceeded.
    """

class InvalidEnumeratedParameter(AWSError):
    pass


