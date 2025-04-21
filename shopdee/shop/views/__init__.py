from .home import HomePageView, ExploreView
from .collection import CollectionDetailView
from .product import ProductSelectSizeView, ShowProductByConditionView, ProductReviewView
from .profile import ProfileView, EditProfileView, ChangePasswordView
from .address import AddressView, NewAddressView, EditAddressView, DeleteAddressView
from .cart import CartView, AddToCartView, RemoveFromCartView, ClearCartView, CheckoutCartView
from .checkout import ProductCheckoutView, PaymentSuccessView
from .wishlist import WishListView, AddToWishlistView, RemoveFromWishlistView
from .order import OrderDetailView, BuyingView
from .selling import SellingView, SellingDetailView, SellDetailView, SellSummaryView
from .api import GetDistrictsView, GetSubdistrictsView