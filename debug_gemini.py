{% extends 'base.html' %}

{% block content %}
<div class="auth-container">
    <h2>Welcome Back</h2>
    <form method="POST" class="auth-form">
        <div class="form-group">
            <label>Username</label>
            <input type="text" name="username" required placeholder="Enter your username">
        </div>
        <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" required placeholder="Enter your password">
        </div>
        <div class="form-group">
            <label>Login As</label>
            <select name="role" class="role-select">
                <option value="Student">Student</option>
                <option value="Teacher">Teacher</option>
                <option value="Parent">Parent</option>
            </select>
        </div>
        <button type="submit" class="btn-primary">Login</button>
    </form>
    <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
</div>
{% endblock %}
