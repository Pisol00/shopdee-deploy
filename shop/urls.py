from django.urls import path

from . import views


urlpatterns = [
    path("", views.HomePageView.as_view(), name="homepage"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("address/", views.AddressView.as_view(), name="address"),
    path("newaddress/", views.NewAddressView.as_view(), name="newaddress"),
    path('editaddress/<int:address_id>/', views.EditAddressView.as_view(), name='edit_address'),
    path('deleteaddress/<int:address_id>/', views.DeleteAddressView.as_view(), name='delete_address'),
    path("editprofile/", views.EditProfileView.as_view(), name="edit_profile"),
    path("buying/", views.BuyingView.as_view(), name="buying"),
    path("selling/", views.SellingView.as_view(), name="selling"),
    path("change_password/", views.ChangePasswordView.as_view(), name="change_password"),
    path("wishlist/", views.WishListView.as_view(), name="wishlist"),
    path('wishlist/add/<int:collection_id>/', views.AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/check/<int:collection_id>/', views.AddToWishlistView.as_view(), name='check_wishlist'),
    path('wishlist/remove/<int:collection_id>/', views.RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    
    
    path('get_districts/<int:province_id>/', views.GetDistrictsView.as_view(), name='get_districts'),
    path('get_subdistricts/<int:district_id>/', views.GetSubdistrictsView.as_view(), name='get_subdistricts'),
    
    
    path("explore/", views.ExploreView.as_view(), name="explore"),
    path("collection/<int:collection_id>/", views.CollectionDetailView.as_view(), name="detail"),
    path('sell_list/', views.SizelistView.as_view(), name='sell_list'),
    
    path('product/<int:product_id>/review/', views.ProductReviewView.as_view(), name='product_review'),
    
    
    path("product_bid/", views.ProductBidView.as_view(), name="product_bid"),
    path("product_checkout/", views.ProductCheckoutView.as_view(), name="product_checkout"),
    path("product_size/<int:collection_id>/", views.ProductSelectSizeView.as_view(), name="product_size"),
    path("show-product-by-condition/", views.ShowProductByConditionView.as_view(), name="product_size"),
    
    path('check_stock/', views.ProductSelectSizeView.as_view(), name='check_stock'),
    
    path('payment/success/<int:payment_id>/', views.PaymentSuccessView.as_view(), name='payment_success'),
    
    path('sell_detail/', views.SellDetailView.as_view(), name='sell_detail'),
    path('sell_detail/sell_summary/', views.SellSummaryView.as_view(), name='sell_summary'),
    
    path('order/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('selling/<int:selling_id>/', views.SellingDetailView.as_view(), name='selling_detail'),
]
