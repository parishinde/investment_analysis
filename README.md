# Real Estate Investment Advisor Platform

A comprehensive web-based application for analyzing real estate properties and providing data-driven investment recommendations based on investor profiles and financial metrics.

## 🎯 Features

### Core Functionality

- **Property Management**: Store and manage detailed property information including location, price, rental income, maintenance costs, size, and risk level
- **Investment Metrics**: Automatic calculation of key indicators:
  - Annual Rental Income
  - Rental Yield (%)
  - Net ROI (%)
  - Price per square foot
  - Maintenance ratio

### Investor Profiles

- **Predefined Profiles**:

  - Conservative End-User
  - Balanced Rental Investor
  - Aggressive Growth Investor
  - Premium Long-term Holder
  - Value-Add Specialist

- **Custom Profile Creation**: Define your own investment criteria:
  - Budget range (min/max)
  - Risk tolerance (Low/Medium/High)
  - Minimum rental yield target
  - Minimum ROI target
  - Preferred locations

### Intelligent Recommendation Engine

- **Multi-factor Scoring System** (0-100 points):

  - Price fit analysis (25 points)
  - Risk alignment (20 points)
  - Rental yield performance (30 points)
  - Net ROI performance (25 points)
  - Location preference bonus (up to 10 points)

- **Transparent Reasoning**: Each recommendation includes detailed analysis explaining:
  - How the property matches investor criteria
  - Specific strengths and weaknesses
  - Performance metrics comparison
  - Risk assessment

### Additional Tools

- **Property Comparison**: Side-by-side comparison of up to 4 properties
- **Market Analytics**: Statistical insights and distributions by:
  - Risk level
  - Property type
  - Location
- **Property Addition**: Add new properties to the database
- **Recommendation History**: Track past recommendations

## 🛠️ Technology Stack

### Backend

- **Python 3.x**
- **Flask**: Lightweight web framework
- **SQLite**: Embedded database for property storage
- **Flask-CORS**: Cross-origin resource sharing support

### Frontend

- **HTML5/CSS3**: Modern, responsive design
- **Vanilla JavaScript**: No dependencies, pure JS
- **Responsive Layout**: Mobile-friendly interface

## 📋 Requirements

```txt
Flask==3.0.0
flask-cors==4.0.0
Python 3.7+
```

## 🚀 Installation & Setup

### 1. Clone or Download the Project

```bash
cd /path/to/project
cd real_estate_advisor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 4. Access the Platform

Open your web browser and navigate to:

```
http://localhost:5000
```

## 📊 Database Schema

### Properties Table

```sql
- id: INTEGER PRIMARY KEY
- name: TEXT (property name)
- location: TEXT
- price: REAL
- size: REAL (square feet)
- annual_rental_income: REAL
- maintenance_cost: REAL
- risk_level: TEXT (Low/Medium/High)
- property_type: TEXT
- year_built: INTEGER
- description: TEXT
- created_at: TIMESTAMP
```

### Investor Profiles Table

```sql
- id: INTEGER PRIMARY KEY
- name: TEXT
- budget_min: REAL
- budget_max: REAL
- risk_tolerance: TEXT (Low/Medium/High)
- investment_horizon: TEXT
- preferred_locations: TEXT
- min_rental_yield: REAL
- min_roi: REAL
- created_at: TIMESTAMP
```

### Recommendations Table

```sql
- id: INTEGER PRIMARY KEY
- investor_profile_id: INTEGER (FK)
- property_id: INTEGER (FK)
- rental_yield: REAL
- net_roi: REAL
- score: REAL
- reasoning: TEXT
- created_at: TIMESTAMP
```

## 🔍 API Endpoints

### Properties

- `GET /api/properties` - List all properties with metrics
- `GET /api/properties/<id>` - Get single property details
- `POST /api/properties` - Add new property

### Investor Profiles

- `GET /api/investor-profiles` - List all profiles
- `GET /api/investor-profiles/<id>` - Get single profile
- `POST /api/investor-profiles` - Add new profile

### Recommendations

- `POST /api/recommendations` - Generate investment recommendations
  - Body: `{profile_id: int}` or `{custom_profile: {...}}`
  - Returns: Ranked list of properties with scores and reasoning

### Comparison & Analytics

- `POST /api/compare` - Compare multiple properties
  - Body: `{property_ids: [int, int, ...]}`
- `GET /api/analytics` - Market statistics and distributions

## 📱 User Interface

### 1. Get Recommendations Tab

- Select predefined investor profile or create custom profile
- Generate ranked recommendations with detailed analysis
- View investment scores, metrics, and reasoning

### 2. Browse Properties Tab

- View all available properties in grid layout
- See key metrics at a glance (rental yield, ROI)
- Filter by risk level and property type

### 3. Compare Properties Tab

- Select 2-4 properties for side-by-side comparison
- Compare all metrics in tabular format
- Identify best value propositions

### 4. Market Analytics Tab

- Overall market statistics
- Distribution analysis by risk, type, and location
- Average price insights

### 5. Add Property Tab

- Comprehensive form for new property entry
- Validation and error handling
- Immediate feedback on submission

### 6. Investor Profiles Tab

- View all predefined investor profiles
- See detailed criteria for each profile type

## 🧮 Investment Calculations

### Rental Yield Formula

```
Rental Yield (%) = (Annual Rental Income / Property Price) × 100
```

### Net ROI Formula

```
Net Income = Annual Rental Income - Maintenance Cost
Net ROI (%) = (Net Income / Property Price) × 100
```

### Investment Score Calculation

The scoring algorithm evaluates properties on multiple dimensions:

1. **Price Fit (25 points)**

   - Perfect fit: 25 points
   - Partial fit: Scaled reduction based on deviation

2. **Risk Alignment (20 points)**

   - Perfect match: 20 points
   - Partial match: 10-15 points
   - Mismatch: 5-10 points

3. **Rental Yield Performance (30 points)**

   - Meets or exceeds target: 20-30 points
   - Below target: Scaled reduction

4. **Net ROI Performance (25 points)**

   - Meets or exceeds target: 15-25 points
   - Below target: Scaled reduction

5. **Location Bonus (10 points)**
   - Matches preferred locations: +10 points

## 🎨 Design Principles

### 1. Transparency

- All calculations are explicit and documented
- Reasoning for recommendations is clearly explained
- Metrics are prominently displayed

### 2. Client-Centric

- Recommendations based on individual investor profiles
- Customizable criteria
- Multiple profile types for different investment strategies

### 3. Data-Driven

- Objective scoring based on quantitative metrics
- No arbitrary rankings
- Statistical market insights

### 4. Ethical Decision-Making

- No hidden fees or commissions
- Equal treatment of all properties
- Risk levels clearly disclosed

## 🔒 Security Considerations

- Input validation on all forms
- SQL injection prevention through parameterized queries
- CORS protection for API endpoints
- No sensitive data exposure

## 🚀 Future Enhancements

Potential features for expansion:

- User authentication and personal portfolios
- Historical price trends and market predictions
- Mortgage calculator integration
- Property image uploads
- Email notifications for new opportunities
- Advanced filtering and search
- Export recommendations to PDF
- Integration with real estate APIs
- Machine learning for price prediction
- Multi-currency support

## 📝 Sample Data

The application includes 10 sample properties representing various:

- Price ranges: $120K - $1.2M
- Property types: Apartments, houses, condos, villas, commercial
- Risk levels: Low, medium, high
- Locations: Urban, suburban, coastal, emerging

And 5 predefined investor profiles covering:

- Budget ranges: $100K - $1.5M
- Risk tolerances: Low to high
- Investment horizons: Short-term to long-term

## 🤝 Contributing

This is an educational project demonstrating:

- Full-stack web development
- RESTful API design
- Database modeling
- Investment analysis algorithms
- Responsive UI/UX design

## 📄 License

This project is designed for educational and demonstration purposes. Feel free to use it as a learning resource or foundation for your own projects.

## 👨‍💻 Development Notes

### Code Structure

```
real_estate_advisor/
├── app.py                 # Flask backend with all API routes
├── templates/
│   └── index.html        # Single-page application frontend
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── real_estate.db        # SQLite database (auto-generated)
```

### Running in Production

For production deployment, consider:

- Using Gunicorn or uWSGI instead of Flask dev server
- PostgreSQL or MySQL instead of SQLite
- Environment variables for configuration
- HTTPS/SSL certificates
- Load balancing for scalability
- Caching layer (Redis)
- CDN for static assets

---

**Built with ❤️ for real estate investors and data enthusiasts**
