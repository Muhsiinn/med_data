# 🩺 Klinikum Report Editor

A comprehensive Flask web application to manage and edit your Klinikum mental health report data with **customizable fields**.

## ✨ Features

- 📊 **View all entries** in a clean, responsive table
- 📈 **Interactive graphs** - Visualize your data with 9+ chart types
- 📄 **PDF Export** - Download complete report with graphs and notes
- ✏️ **Edit existing entries** with full validation
- ➕ **Add new entries** easily
- 🗑️ **Delete entries** with confirmation
- ⚙️ **Customize fields** - Add, remove, or modify tracked metrics
- 🎯 **Auto-graph custom fields** - New numeric fields appear in graphs automatically
- 💾 **Auto-save** to CSV file
- 🎨 **Beautiful UI** with gradient background and smooth animations
- 📱 **Mobile responsive** design

## 🆕 New Fields Added by Default

In addition to the original fields, the app now includes:
- **Energy Level** (1-10)
- **Appetite** (1-10)
- **Social Interaction** (1-10)
- **Exercise Minutes** (0+)
- **Therapy Session** (text notes)

## 📦 Installation

1. **Navigate to the project folder:**
```bash
cd klinikum_editor
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 🚀 Usage

1. **Start the application:**
```bash
python app.py
```

2. **Open your browser:**
```
http://localhost:5000
```

3. **Available pages:**
   - **Home** - View all entries in table format
   - **Graphs** - Visual analytics and charts
   - **Add Entry** - Create new entries
   - **Edit Entry** - Modify existing entries
   - **Manage Fields** - Customize tracked metrics

## 📈 Available Visualizations

The Graphs page automatically generates visualizations based on your data:

1. **Mood, Panic, and Headache Trends** - Track core mental health metrics
2. **Medication Tracking** - Monitor dosage changes over time
3. **Headache vs Medication** - Correlation between headache and meds
4. **Wellness Tracking** - Energy, appetite, and social interaction
5. **Sleep Pattern** - Sleep hours with recommended baseline
6. **Correlation Matrix** - Relationships between all metrics
7. **Exercise Log** - Activity tracking (if enabled)
8. **Emotional Well-being** - Mood vs hope comparison
9. **Custom Fields Tracking** - Auto-graphs any custom numeric fields you add!

Graphs update automatically when you add or modify data!

## 📄 PDF Export

Click **"Export PDF"** to download a comprehensive report containing:

- **Summary statistics** - Average, min, max for all metrics
- **Key visualizations** - Core symptom trends and sleep patterns
- **Complete daily notes** - All your journal entries formatted beautifully
- **Auto-generated filename** - Timestamped for easy organization

Perfect for sharing with your therapist or doctor!

## ⚙️ Field Management

### Adding Custom Fields

1. Click **"Manage Fields"** in the top navigation
2. Fill in the "Add New Field" form:
   - **Field Name**: Internal identifier (e.g., `stress_level`)
   - **Field Label**: Display name (e.g., "Stress Level")
   - **Field Type**: number, text, date, or textarea
   - **Min/Max Values**: For number fields
   - **Required**: Check if mandatory
3. Click **"Add Field"**

### Deleting Fields

- Each field (except `date` and `notes`) has a **Delete** button
- Deleting a field hides it from forms but preserves data in CSV
- You can restore default fields anytime

### Resetting Fields

- Click **"Reset to Default Fields"** to restore original configuration
- This doesn't delete your data, only resets field definitions

## 📁 File Structure

```
klinikum_editor/
├── app.py                      # Main Flask application
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── index.html             # View all entries
│   ├── edit.html              # Edit entry form
│   ├── add.html               # Add new entry form
│   └── fields.html            # Field management page
├── static/
│   └── css/
│       └── style.css          # Custom styling
├── klinikum_4weeks.csv        # Your data (auto-created)
├── fields_config.json         # Field configuration (auto-created)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 📊 Data Fields (Default)

### Core Metrics
- Date
- Mood Score (1-10)
- Panic Intensity (1-10)
- Headache Intensity (1-10)
- Sleep Hours (0-24)
- Hope Score (1-10)
- Sedation Feeling (1-10)

### Medications
- Medication 1-4 (mg)

### New Wellness Metrics
- Energy Level (1-10)
- Appetite (1-10)
- Social Interaction (1-10)
- Exercise Minutes
- Therapy Session notes

### Notes
- Daily observations and notes

## 💡 Tips

- **Backup your CSV** before major edits
- **Use descriptive field names** when adding custom fields
- **Set min/max values** for number fields to ensure data quality
- **Mark important fields as required** to prevent missing data
- **Export data** regularly for analysis in other tools

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal to stop the Flask server.

## 🔒 Data Privacy

- All data is stored locally in `klinikum_4weeks.csv`
- No data is sent to external servers
- The app runs entirely on your machine

## 🐛 Troubleshooting

**CSV not found:**
- Run the Jupyter notebook first cell to create the CSV
- Or add your first entry manually

**Fields not showing:**
- Check `fields_config.json` exists
- Click "Reset to Default Fields" to restore

**Changes not saving:**
- Check file permissions in the folder
- Ensure CSV is not open in another program

## 📄 License

Free to use for personal health tracking.
