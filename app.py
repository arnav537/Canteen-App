{% extends 'base.html' %}

{% block content %}
<div class="cart-container">
    <h2>Your Cart</h2>
    <div id="cart-items" class="cart-items">
        <!-- JS will populate this -->
        <p>Your cart is empty.</p>
    </div>

    <div class="cart-summary" id="cart-summary" style="display:none;">
        <div class="total">Total: ₹<span id="cart-total">0</span></div>
        <div class="actions">
            <button onclick="checkout('Vend Receipt')" class="btn-vend">Vend Receipt</button>
            <button onclick="checkout('Place Order')" class="btn-place">Place Order</button>
        </div>
    </div>
</div>

<script>
    // Cart logic embedded for simplicity in MVP
    function loadCart() {
        const cart = JSON.parse(sessionStorage.getItem('cart') || '[]');
        const container = document.getElementById('cart-items');
        const summary = document.getElementById('cart-summary');

        if (cart.length === 0) {
            container.innerHTML = '<p>Your cart is empty.</p>';
            summary.style.display = 'none';
            return;
        }

        container.innerHTML = '';
        let total = 0;

        cart.forEach((item, index) => {
            total += item.price * item.quantity;
            const div = document.createElement('div');
            div.className = 'cart-item';
            div.innerHTML = `
                <span>${item.name} (x${item.quantity})</span>
                <span>₹${item.price * item.quantity}</span>
                <button onclick="removeFromCart(${index})" class="btn-remove">Remove</button>
            `;
            container.appendChild(div);
        });

        document.getElementById('cart-total').innerText = total;
        summary.style.display = 'block';
    }

    function removeFromCart(index) {
        const cart = JSON.parse(sessionStorage.getItem('cart') || '[]');
        cart.splice(index, 1);
        sessionStorage.setItem('cart', JSON.stringify(cart));
        loadCart();
        updateCartCount(); // Defined in main.js or here
    }

    function checkout(type) {
        const cart = JSON.parse(sessionStorage.getItem('cart') || '[]');
        if (cart.length === 0) return;

        fetch('{{ url_for("checkout") }}', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type, items: cart })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    sessionStorage.removeItem('cart');
                    window.location.href = '{{ url_for("order_history") }}';
                } else {
                    alert('Error: ' + data.message);
                }
            });
    }

    window.addEventListener('load', loadCart);
</script>
{% endblock %}