from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = 'real_estate.db'

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables and sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create properties table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            price REAL NOT NULL,
            size REAL NOT NULL,
            annual_rental_income REAL NOT NULL,
            maintenance_cost REAL NOT NULL,
            risk_level TEXT NOT NULL,
            property_type TEXT NOT NULL,
            year_built INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create investor profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investor_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            budget_min REAL NOT NULL,
            budget_max REAL NOT NULL,
            risk_tolerance TEXT NOT NULL,
            investment_horizon TEXT NOT NULL,
            preferred_locations TEXT,
            min_rental_yield REAL,
            min_roi REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create recommendations history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investor_profile_id INTEGER,
            property_id INTEGER,
            rental_yield REAL,
            net_roi REAL,
            score REAL,
            reasoning TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investor_profile_id) REFERENCES investor_profiles (id),
            FOREIGN KEY (property_id) REFERENCES properties (id)
        )
    ''')
    
    # Check if sample data already exists
    cursor.execute('SELECT COUNT(*) FROM properties')
    if cursor.fetchone()[0] == 0:
        # Insert sample properties
        sample_properties = [
            ('Downtown Luxury Apartment', 'Downtown City Center', 450000, 1200, 36000, 4500, 'Low', 'Apartment', 2020, 'Modern luxury apartment in prime location with high demand'),
            ('Suburban Family Home', 'Green Valley Suburbs', 320000, 2000, 28800, 6400, 'Low', 'House', 2015, 'Spacious family home in growing suburban area'),
            ('Beachfront Condo', 'Coastal Beach Area', 580000, 1500, 52200, 8700, 'Medium', 'Condo', 2018, 'Premium beachfront property with vacation rental potential'),
            ('Urban Studio', 'University District', 180000, 600, 18000, 2700, 'Medium', 'Studio', 2019, 'Compact studio near university, high student demand'),
            ('Commercial Office Space', 'Business District', 750000, 3000, 75000, 15000, 'Medium', 'Commercial', 2017, 'Prime office space with corporate tenants'),
            ('Fixer-Upper Duplex', 'Emerging Neighborhood', 220000, 1800, 21600, 8800, 'High', 'Duplex', 1995, 'Value-add opportunity in gentrifying area'),
            ('Luxury Villa', 'Hillside Estates', 1200000, 4500, 84000, 18000, 'Low', 'Villa', 2021, 'Premium villa with panoramic views'),
            ('Budget Apartment', 'Industrial Zone', 120000, 500, 12000, 3600, 'High', 'Apartment', 2005, 'Affordable entry-level investment property'),
            ('Mid-Rise Condo', 'Metro Center', 380000, 1100, 38000, 5700, 'Low', 'Condo', 2019, 'Well-maintained condo with metro access'),
            ('Townhouse', 'Family District', 425000, 2200, 40800, 6800, 'Low', 'Townhouse', 2016, 'Modern townhouse in family-friendly neighborhood')
        ]
        
        cursor.executemany('''
            INSERT INTO properties (name, location, price, size, annual_rental_income, 
                                   maintenance_cost, risk_level, property_type, year_built, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_properties)
    
    # Check if investor profiles already exist
    cursor.execute('SELECT COUNT(*) FROM investor_profiles')
    if cursor.fetchone()[0] == 0:
        # Insert predefined investor profiles
        sample_profiles = [
            ('Conservative End-User', 200000, 500000, 'Low', 'Long-term (10+ years)', 'Suburbs, Family District', 5.0, 3.0),
            ('Balanced Rental Investor', 150000, 600000, 'Medium', 'Medium-term (5-10 years)', 'Downtown, Metro Center', 7.0, 5.0),
            ('Aggressive Growth Investor', 100000, 400000, 'High', 'Short-term (1-5 years)', 'Emerging, University', 10.0, 8.0),
            ('Premium Long-term Holder', 500000, 1500000, 'Low', 'Long-term (10+ years)', 'Hillside, Coastal', 6.0, 4.0),
            ('Value-Add Specialist', 150000, 350000, 'High', 'Medium-term (5-10 years)', 'Emerging, Industrial', 12.0, 10.0)
        ]
        
        cursor.executemany('''
            INSERT INTO investor_profiles (name, budget_min, budget_max, risk_tolerance, 
                                          investment_horizon, preferred_locations, min_rental_yield, min_roi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_profiles)
    
    conn.commit()
    conn.close()

# Investment calculation functions
def calculate_rental_yield(annual_rental_income, property_price):
    """Calculate rental yield percentage"""
    return (annual_rental_income / property_price) * 100

def calculate_net_roi(annual_rental_income, maintenance_cost, property_price):
    """Calculate net ROI percentage"""
    net_income = annual_rental_income - maintenance_cost
    return (net_income / property_price) * 100

def calculate_investment_score(property, profile):
    """
    Calculate investment score based on multiple factors
    Score range: 0-100
    """
    score = 0
    reasoning_parts = []
    
    # Price fit (25 points)
    if profile['budget_min'] <= property['price'] <= profile['budget_max']:
        price_fit = 25
        reasoning_parts.append(f"✓ Price ${property['price']:,.0f} fits budget range")
    else:
        price_ratio = property['price'] / profile['budget_max'] if property['price'] > profile['budget_max'] else profile['budget_min'] / property['price']
        price_fit = max(0, 25 - (price_ratio - 1) * 50)
        if property['price'] > profile['budget_max']:
            reasoning_parts.append(f"⚠ Price exceeds budget by {((property['price']/profile['budget_max']-1)*100):.1f}%")
        else:
            reasoning_parts.append(f"⚠ Price below minimum budget")
    score += price_fit
    
    # Risk alignment (20 points)
    risk_match = {
        'Low': {'Low': 20, 'Medium': 10, 'High': 5},
        'Medium': {'Low': 15, 'Medium': 20, 'High': 15},
        'High': {'Low': 10, 'Medium': 15, 'High': 20}
    }
    risk_score = risk_match[profile['risk_tolerance']][property['risk_level']]
    score += risk_score
    
    if risk_score == 20:
        reasoning_parts.append(f"✓ Risk level ({property['risk_level']}) matches investor tolerance")
    else:
        reasoning_parts.append(f"⚠ Risk level ({property['risk_level']}) partially matches tolerance")
    
    # Rental yield performance (30 points)
    rental_yield = calculate_rental_yield(property['annual_rental_income'], property['price'])
    if rental_yield >= profile['min_rental_yield']:
        yield_excess = rental_yield - profile['min_rental_yield']
        yield_score = min(30, 20 + yield_excess * 2)
        reasoning_parts.append(f"✓ Rental yield {rental_yield:.2f}% exceeds minimum by {yield_excess:.2f}%")
    else:
        yield_gap = profile['min_rental_yield'] - rental_yield
        yield_score = max(0, 20 - yield_gap * 3)
        reasoning_parts.append(f"⚠ Rental yield {rental_yield:.2f}% below target by {yield_gap:.2f}%")
    score += yield_score
    
    # Net ROI performance (25 points)
    net_roi = calculate_net_roi(property['annual_rental_income'], property['maintenance_cost'], property['price'])
    if net_roi >= profile['min_roi']:
        roi_excess = net_roi - profile['min_roi']
        roi_score = min(25, 15 + roi_excess * 2)
        reasoning_parts.append(f"✓ Net ROI {net_roi:.2f}% exceeds minimum by {roi_excess:.2f}%")
    else:
        roi_gap = profile['min_roi'] - net_roi
        roi_score = max(0, 15 - roi_gap * 3)
        reasoning_parts.append(f"⚠ Net ROI {net_roi:.2f}% below target by {roi_gap:.2f}%")
    score += roi_score
    
    # Location preference bonus (up to 10 points)
    location_bonus = 0
    if profile['preferred_locations']:
        preferred_locs = [loc.strip().lower() for loc in profile['preferred_locations'].split(',')]
        property_loc = property['location'].lower()
        if any(pref in property_loc for pref in preferred_locs):
            location_bonus = 10
            reasoning_parts.append(f"✓ Location matches preferences")
    
    score += location_bonus
    
    return min(100, score), reasoning_parts

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/properties', methods=['GET'])
def get_properties():
    """Get all properties with calculated metrics"""
    conn = get_db_connection()
    properties = conn.execute('SELECT * FROM properties ORDER BY price').fetchall()
    conn.close()
    
    result = []
    for prop in properties:
        prop_dict = dict(prop)
        prop_dict['rental_yield'] = calculate_rental_yield(
            prop['annual_rental_income'], 
            prop['price']
        )
        prop_dict['net_roi'] = calculate_net_roi(
            prop['annual_rental_income'],
            prop['maintenance_cost'],
            prop['price']
        )
        result.append(prop_dict)
    
    return jsonify(result)

@app.route('/api/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    """Get single property details"""
    conn = get_db_connection()
    prop = conn.execute('SELECT * FROM properties WHERE id = ?', (property_id,)).fetchone()
    conn.close()
    
    if prop is None:
        return jsonify({'error': 'Property not found'}), 404
    
    prop_dict = dict(prop)
    prop_dict['rental_yield'] = calculate_rental_yield(prop['annual_rental_income'], prop['price'])
    prop_dict['net_roi'] = calculate_net_roi(prop['annual_rental_income'], prop['maintenance_cost'], prop['price'])
    
    return jsonify(prop_dict)

@app.route('/api/properties', methods=['POST'])
def add_property():
    """Add new property"""
    data = request.json
    
    required_fields = ['name', 'location', 'price', 'size', 'annual_rental_income', 
                       'maintenance_cost', 'risk_level', 'property_type']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO properties (name, location, price, size, annual_rental_income, 
                               maintenance_cost, risk_level, property_type, year_built, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['location'], data['price'], data['size'],
        data['annual_rental_income'], data['maintenance_cost'], data['risk_level'],
        data['property_type'], data.get('year_built'), data.get('description')
    ))
    
    property_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': property_id, 'message': 'Property added successfully'}), 201

@app.route('/api/investor-profiles', methods=['GET'])
def get_profiles():
    """Get all investor profiles"""
    conn = get_db_connection()
    profiles = conn.execute('SELECT * FROM investor_profiles').fetchall()
    conn.close()
    
    return jsonify([dict(profile) for profile in profiles])

@app.route('/api/investor-profiles/<int:profile_id>', methods=['GET'])
def get_profile(profile_id):
    """Get single investor profile"""
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM investor_profiles WHERE id = ?', (profile_id,)).fetchone()
    conn.close()
    
    if profile is None:
        return jsonify({'error': 'Profile not found'}), 404
    
    return jsonify(dict(profile))

@app.route('/api/investor-profiles', methods=['POST'])
def add_profile():
    """Add new investor profile"""
    data = request.json
    
    required_fields = ['name', 'budget_min', 'budget_max', 'risk_tolerance', 
                       'investment_horizon', 'min_rental_yield', 'min_roi']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO investor_profiles (name, budget_min, budget_max, risk_tolerance, 
                                       investment_horizon, preferred_locations, min_rental_yield, min_roi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['budget_min'], data['budget_max'], data['risk_tolerance'],
        data['investment_horizon'], data.get('preferred_locations', ''),
        data['min_rental_yield'], data['min_roi']
    ))
    
    profile_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': profile_id, 'message': 'Profile added successfully'}), 201

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Generate investment recommendations based on investor profile"""
    data = request.json
    profile_id = data.get('profile_id')
    custom_profile = data.get('custom_profile')
    top_n = data.get('top_n', 5)
    
    conn = get_db_connection()
    
    # Get investor profile
    if profile_id:
        profile = conn.execute('SELECT * FROM investor_profiles WHERE id = ?', (profile_id,)).fetchone()
        if not profile:
            conn.close()
            return jsonify({'error': 'Profile not found'}), 404
        profile = dict(profile)
    elif custom_profile:
        profile = custom_profile
    else:
        conn.close()
        return jsonify({'error': 'Profile ID or custom profile required'}), 400
    
    # Get all properties
    properties = conn.execute('SELECT * FROM properties').fetchall()
    
    # Calculate scores for each property
    recommendations = []
    for prop in properties:
        prop_dict = dict(prop)
        prop_dict['rental_yield'] = calculate_rental_yield(
            prop['annual_rental_income'], 
            prop['price']
        )
        prop_dict['net_roi'] = calculate_net_roi(
            prop['annual_rental_income'],
            prop['maintenance_cost'],
            prop['price']
        )
        
        score, reasoning_parts = calculate_investment_score(prop_dict, profile)
        
        recommendations.append({
            'property': prop_dict,
            'score': score,
            'reasoning': reasoning_parts,
            'rental_yield': prop_dict['rental_yield'],
            'net_roi': prop_dict['net_roi']
        })
    
    # Sort by score
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    # Store top recommendations in history
    cursor = conn.cursor()
    for rec in recommendations[:top_n]:
        cursor.execute('''
            INSERT INTO recommendations (investor_profile_id, property_id, rental_yield, 
                                        net_roi, score, reasoning)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            profile.get('id'),
            rec['property']['id'],
            rec['rental_yield'],
            rec['net_roi'],
            rec['score'],
            '\n'.join(rec['reasoning'])
        ))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'profile': profile,
        'recommendations': recommendations[:top_n],
        'total_analyzed': len(recommendations)
    })

@app.route('/api/compare', methods=['POST'])
def compare_properties():
    """Compare multiple properties side by side"""
    data = request.json
    property_ids = data.get('property_ids', [])
    
    if not property_ids:
        return jsonify({'error': 'Property IDs required'}), 400
    
    conn = get_db_connection()
    properties = []
    
    for prop_id in property_ids:
        prop = conn.execute('SELECT * FROM properties WHERE id = ?', (prop_id,)).fetchone()
        if prop:
            prop_dict = dict(prop)
            prop_dict['rental_yield'] = calculate_rental_yield(
                prop['annual_rental_income'], 
                prop['price']
            )
            prop_dict['net_roi'] = calculate_net_roi(
                prop['annual_rental_income'],
                prop['maintenance_cost'],
                prop['price']
            )
            prop_dict['price_per_sqft'] = prop['price'] / prop['size']
            prop_dict['maintenance_ratio'] = (prop['maintenance_cost'] / prop['annual_rental_income']) * 100
            properties.append(prop_dict)
    
    conn.close()
    
    return jsonify({'properties': properties})

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get market analytics and statistics"""
    conn = get_db_connection()
    
    # Overall statistics
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_properties,
            AVG(price) as avg_price,
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(annual_rental_income) as avg_rental_income,
            AVG(size) as avg_size
        FROM properties
    ''').fetchone()
    
    # By risk level
    risk_distribution = conn.execute('''
        SELECT risk_level, COUNT(*) as count, AVG(price) as avg_price
        FROM properties
        GROUP BY risk_level
    ''').fetchall()
    
    # By property type
    type_distribution = conn.execute('''
        SELECT property_type, COUNT(*) as count, AVG(price) as avg_price
        FROM properties
        GROUP BY property_type
    ''').fetchall()
    
    # By location
    location_distribution = conn.execute('''
        SELECT location, COUNT(*) as count, AVG(price) as avg_price
        FROM properties
        GROUP BY location
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'overall': dict(stats),
        'by_risk': [dict(row) for row in risk_distribution],
        'by_type': [dict(row) for row in type_distribution],
        'by_location': [dict(row) for row in location_distribution]
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)