{% extends 'base.html' %}

{% block content %}
<div class="history-container">
    <h2>Order History</h2>
    {% if orders %}
    <table class="history-table">
        <thead>
            <tr>
                <th>Date</th>
                <th>Order ID</th>
                <th>Items</th>
                <th>Type</th>
                <th>Total</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>{{ order.created_at }}</td>
                <td>#{{ order.id }}</td>
                <td>{{ order.ordered_items }}</td>
                <td>₹{{ order.total_amount }}</td>
                <td>{{ order.status }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p>No orders yet.</p>
    {% endif %}
</div>
{% endblock %}