
function addToWishlist(collectionId) {
    fetch(`/wishlist/add/${collectionId}/`, {
        method: "GET",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
        },
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.status === "added") {
            Swal.fire({
                icon: "success",
                title: "Added to Wishlist",
                text: "This item has been added to your wishlist.",
                showConfirmButton: false,
                timer: 1500,
            });
        } else if (data.status === "already_added") {
            Swal.fire({
                icon: "warning",
                title: "Already in Wishlist",
                text: "This item is already in your wishlist.",
                showConfirmButton: true,
            });
        }
    })
    .catch((error) => {
        console.error('Error adding to wishlist:', error);
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "There was an error adding the item to your wishlist. Please try again.",
            showConfirmButton: true,
        });
    });
}

