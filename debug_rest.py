{% extends 'base.html' %}

{% block content %}
<section class="hero">
    <h2>Fuel Your Day with Freshness</h2>
    <p>Discover healthy, delicious, and budget-friendly meals right here on campus.</p>
</section>

<!-- Search is now in header, but we keep filters here -->
<div class="filter-pills">
    <button class="filter-btn active" data-filter="all">All</button>
    <button class="filter-btn" data-filter="veg">Veg</button>
    <button class="filter-btn" data-filter="non-veg">Non-Veg</button>
    <button class="filter-btn" data-filter="beverage">Beverages</button>
    <button class="filter-btn" data-filter="biryani">Biryani</button>
    <button class="filter-btn" data-filter="burger">Burger</button>
    <button class="filter-btn" data-filter="chaat">Chaat</button>
    <button class="filter-btn" data-filter="chinese">Chinese</button>
    <button class="filter-btn" data-filter="combos">Combos</button>
    <button class="filter-btn" data-filter="dessert">Dessert</button>
    <button class="filter-btn" data-filter="dosa">Dosa</button>
    <button class="filter-btn" data-filter="energy">Energy Drink</button>
    <button class="filter-btn" data-filter="maggi">Maggi</button>
    <button class="filter-btn" data-filter="meals">Meals</button>
    <button class="filter-btn" data-filter="momo">Momo</button>
    <button class="filter-btn" data-filter="north-indian">North Indian</button>
    <button class="filter-btn" data-filter="pizza">Pizza</button>
    <button class="filter-btn" data-filter="rolls">Rolls</button>
    <button class="filter-btn" data-filter="snacks">Snacks</button>
</div>
</div>

<div class="menu-grid">
    {% for item in items %}
    <div class="menu-item" data-tags='{{ item.tags }}'>
        <div class="item-visuals">
            <!-- Choice Badge Logic -->
            {% if 'amber' in item.health %}
            <span class="badge-choice badge-amber">AMBER CHOICE</span>
            {% elif 'red' in item.health %}
            <span class="badge-choice badge-red">RED CHOICE</span>
            {% elif 'green' in item.health %}
            <span class="badge-choice badge-green">GREEN CHOICE</span>
            {% endif %}

            <div class="item-header">
                <h3 class="item-name">{{ item.name }}</h3>
                <span class="item-price">₹{{ item.price }}</span>
            </div>

            <div class="item-rating">
                {% for _ in range(item.rating|int) %}★{% endfor %}
                <span style="color:#aaa;">({{ item.rating }})</span>
            </div>
        </div>

        <div class="item-details">
            <div class="nutrition-block">
                {% if 'amber' in item.health %}
                <div class="nutrition-dot health-amber"></div>
                {% elif 'red' in item.health %}
                <div class="nutrition-dot health-red"></div>
                {% else %}
                <div class="nutrition-dot health-green"></div>
                {% endif %}

                <div class="nutrition-vals">
                    <div>{{ item.calories }} <span>kcal</span></div>
                    <div>P: <span>{{ item.protein }}</span></div>
                    <div>C: <span>{{ item.carbs }}</span></div>
                    <div>F: <span>{{ item.fats }}</span></div>
                </div>
            </div>

            <button class="btn-add" data-id="{{ item.id }}" data-name="{{ item.name }}" data-price="{{ item.price }}"
                onclick="addToCart(this.dataset.id, this.dataset.name, this.dataset.price)">
                Add to Cart
            </button>
        </div>
    </div>
    {% else %}
    <p style="text-align:center; width:100%;">No items found.</p>
    {% endfor %}
</div>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        const filterBtns = document.querySelectorAll('.filter-btn');
        const menuItems = document.querySelectorAll('.menu-item');

        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const filter = btn.dataset.filter.toLowerCase();

                menuItems.forEach(item => {
                    const tagsRaw = item.dataset.tags || '[]';
                    let tags = [];
                    try {
                        // Handle potential different formats (string vs already parsed?)
                        // In Jinja template it comes as string representation of list e.g. "['veg', 'momo']"
                        // We replace single quotes with double for valid JSON parsing if needed, 
                        // but Python list string uses single quotes.
                        tags = JSON.parse(tagsRaw.replace(/'/g, '"'));
                    } catch (e) {
                        console.error('Error parsing tags', tagsRaw, e);
                    }

                    // Normalize tags
                    tags = tags.map(t => t.toLowerCase());

                    if (filter === 'all') {
                        item.style.display = 'flex';
                    } else {
                        // Check if tag exists
                        if (tags.includes(filter)) {
                            item.style.display = 'flex';
                        } else {
                            item.style.display = 'none';
                        }
                    }
                });
            });
        });
    });
</script>
{% endblock %}