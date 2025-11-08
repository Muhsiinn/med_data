from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from flask import send_file

app = Flask(__name__)
app.secret_key = 'klinikum_report_secret_key'

CSV_FILE = 'klinikum_4weeks.csv'
FIELDS_CONFIG_FILE = 'fields_config.json'

# Default field configuration
DEFAULT_FIELDS = {
    "date": {"label": "Date", "type": "date", "required": True, "min": None, "max": None},
    "mood_score": {"label": "Mood Score", "type": "number", "required": True, "min": 1, "max": 10},
    "panic_intensity": {"label": "Panic Intensity", "type": "number", "required": True, "min": 1, "max": 10},
    "headache_intensity": {"label": "Headache Intensity", "type": "number", "required": True, "min": 1, "max": 10},
    "sleep_hours": {"label": "Sleep Hours", "type": "number", "required": True, "min": 0, "max": 24},
    "hope_score": {"label": "Hope Score", "type": "number", "required": True, "min": 1, "max": 10},
    "sedation_feeling": {"label": "Sedation Feeling", "type": "number", "required": True, "min": 1, "max": 10},
    "med1_mg": {"label": "Medication 1 (mg)", "type": "number", "required": True, "min": 0, "max": None},
    "med2_mg": {"label": "Medication 2 (mg)", "type": "number", "required": True, "min": 0, "max": None},
    "med3_mg": {"label": "Medication 3 (mg)", "type": "number", "required": True, "min": 0, "max": None},
    "med4_mg": {"label": "Medication 4 (mg)", "type": "number", "required": True, "min": 0, "max": None},
    "energy_level": {"label": "Energy Level", "type": "number", "required": False, "min": 1, "max": 10},
    "appetite": {"label": "Appetite", "type": "number", "required": False, "min": 1, "max": 10},
    "social_interaction": {"label": "Social Interaction", "type": "number", "required": False, "min": 1, "max": 10},
    "exercise_minutes": {"label": "Exercise (minutes)", "type": "number", "required": False, "min": 0, "max": None},
    "therapy_session": {"label": "Therapy Session", "type": "text", "required": False, "min": None, "max": None},
    "notes": {"label": "Notes", "type": "textarea", "required": True, "min": None, "max": None},
    "thoughts": {"label": "Personal Thoughts", "type": "textarea", "required": False, "min": None, "max": None},
    "remarks": {"label": "Remarks", "type": "textarea", "required": False, "min": None, "max": None}
}

def load_fields_config():
    """Load field configuration from JSON file"""
    if os.path.exists(FIELDS_CONFIG_FILE):
        with open(FIELDS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_FIELDS

def save_fields_config(fields):
    """Save field configuration to JSON file"""
    with open(FIELDS_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)

def load_data():
    """Load data from CSV file"""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Ensure all configured fields exist
        fields = load_fields_config()
        for field in fields.keys():
            if field not in df.columns:
                df[field] = '' if fields[field]['type'] == 'text' or fields[field]['type'] == 'textarea' else 0
        return df
    return pd.DataFrame()

def save_data(df):
    """Save data to CSV file"""
    df.to_csv(CSV_FILE, index=False, encoding='utf-8')

@app.route('/')
def index():
    """Display all entries"""
    df = load_data()
    fields = load_fields_config()

    if df.empty:
        flash('No data found. Please add your first entry!', 'warning')
        return render_template('index.html', entries=[], fields=fields)

    entries = df.to_dict('records')
    return render_template('index.html', entries=entries, fields=fields)

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    """Edit a specific entry"""
    df = load_data()
    fields = load_fields_config()

    if request.method == 'POST':
        # Update the entry with all configured fields
        for field_name, field_config in fields.items():
            value = request.form.get(field_name, '')

            if field_config['type'] == 'number':
                try:
                    df.loc[index, field_name] = int(value) if value else 0
                except ValueError:
                    df.loc[index, field_name] = 0
            else:
                df.loc[index, field_name] = value

        save_data(df)
        flash('Entry updated successfully!', 'success')
        return redirect(url_for('index'))

    entry = df.iloc[index].to_dict()
    entry['index'] = index
    return render_template('edit.html', entry=entry, fields=fields)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """Add a new entry"""
    fields = load_fields_config()

    if request.method == 'POST':
        df = load_data()
        new_entry = {}

        for field_name, field_config in fields.items():
            value = request.form.get(field_name, '')

            if field_config['type'] == 'number':
                try:
                    new_entry[field_name] = int(value) if value else 0
                except ValueError:
                    new_entry[field_name] = 0
            else:
                new_entry[field_name] = value

        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(df)
        flash('New entry added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html', fields=fields)

@app.route('/delete/<int:index>')
def delete(index):
    """Delete an entry"""
    df = load_data()
    df = df.drop(index).reset_index(drop=True)
    save_data(df)
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/fields', methods=['GET', 'POST'])
def manage_fields():
    """Manage custom fields"""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            fields = load_fields_config()
            field_name = request.form.get('field_name', '').strip().lower().replace(' ', '_')
            field_label = request.form.get('field_label', '').strip()
            field_type = request.form.get('field_type', 'text')
            field_required = request.form.get('field_required') == 'on'
            field_min = request.form.get('field_min', '')
            field_max = request.form.get('field_max', '')

            if field_name and field_label:
                fields[field_name] = {
                    "label": field_label,
                    "type": field_type,
                    "required": field_required,
                    "min": int(field_min) if field_min else None,
                    "max": int(field_max) if field_max else None
                }
                save_fields_config(fields)

                # Add column to existing data
                df = load_data()
                if not df.empty and field_name not in df.columns:
                    df[field_name] = '' if field_type in ['text', 'textarea'] else 0
                    save_data(df)

                flash(f'Field "{field_label}" added successfully!', 'success')
            else:
                flash('Field name and label are required!', 'danger')

        elif action == 'delete':
            field_to_delete = request.form.get('field_to_delete')
            protected_fields = ['date', 'notes', 'thoughts', 'remarks']
            if field_to_delete and field_to_delete not in protected_fields:
                fields = load_fields_config()
                if field_to_delete in fields:
                    del fields[field_to_delete]
                    save_fields_config(fields)
                    flash(f'Field deleted successfully!', 'success')
            else:
                flash('Cannot delete protected fields (date, notes, thoughts, remarks)!', 'danger')

        return redirect(url_for('manage_fields'))

    fields = load_fields_config()
    return render_template('fields.html', fields=fields)

@app.route('/reset-fields', methods=['POST'])
def reset_fields():
    """Reset fields to default configuration"""
    save_fields_config(DEFAULT_FIELDS)
    flash('Fields reset to default configuration!', 'success')
    return redirect(url_for('manage_fields'))

@app.route('/edit-field/<field_name>', methods=['GET', 'POST'])
def edit_field(field_name):
    """Edit an existing field"""
    fields = load_fields_config()

    if field_name not in fields:
        flash('Field not found!', 'danger')
        return redirect(url_for('manage_fields'))

    if request.method == 'POST':
        field_label = request.form.get('field_label', '').strip()
        field_type = request.form.get('field_type', 'text')
        field_required = request.form.get('field_required') == 'on'
        field_min = request.form.get('field_min', '')
        field_max = request.form.get('field_max', '')

        if field_label:
            fields[field_name] = {
                "label": field_label,
                "type": field_type,
                "required": field_required,
                "min": int(field_min) if field_min else None,
                "max": int(field_max) if field_max else None
            }
            save_fields_config(fields)
            flash(f'Field "{field_label}" updated successfully!', 'success')
            return redirect(url_for('manage_fields'))
        else:
            flash('Field label is required!', 'danger')

    field_config = fields[field_name]
    return render_template('edit_field.html', field_name=field_name, field_config=field_config)

def create_plot_base64(fig):
    """Convert matplotlib figure to base64 string"""
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=150)
    img.seek(0)
    plot_data = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return plot_data

@app.route('/graphs')
def graphs():
    """Display visualizations"""
    df = load_data()

    if df.empty:
        flash('No data available for visualization. Please add entries first.', 'warning')
        return redirect(url_for('index'))

    try:
        # Prepare data
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])  # Remove rows with invalid dates
        df = df.sort_values('date')

        if df.empty:
            flash('No valid date entries found. Please check your data.', 'warning')
            return redirect(url_for('index'))

        # Check if we have numeric columns for medication
        df['total_med_mg'] = 0
        for col in ['med1_mg', 'med2_mg', 'med3_mg', 'med4_mg']:
            if col in df.columns:
                df['total_med_mg'] += pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Set theme - Minimal black and white
        sns.set_theme(style="whitegrid",
                      rc={"axes.facecolor":"#ffffff",
                          "grid.color":"#cccccc",
                          "figure.figsize":(12,6),
                          "axes.edgecolor":"#000000",
                          "axes.linewidth":2,
                          "grid.linewidth":0.5,
                          "xtick.color":"#000000",
                          "ytick.color":"#000000",
                          "text.color":"#000000",
                          "font.family":"monospace"})

        plots = []

        # 1. Mood / Panic / Headache
        if all(col in df.columns for col in ['mood_score', 'panic_intensity', 'headache_intensity']):
            fig1, ax1 = plt.subplots(figsize=(12,6))
            sns.lineplot(df, x='date', y='mood_score', label='Mood', color='#000', lw=2.5, marker='o', ax=ax1)
            sns.lineplot(df, x='date', y='panic_intensity', label='Panic', color='#000', lw=2.5, ls='--', marker='s', ax=ax1)
            sns.lineplot(df, x='date', y='headache_intensity', label='Headache', color='#666', lw=2.5, ls=':', marker='^', ax=ax1)
            ax1.set_title('Mood, Panic, and Headache Over Time', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Date'); ax1.set_ylabel('Score (1-10)')
            ax1.legend(); fig1.tight_layout()
            plots.append({
                'title': 'Mood, Panic, and Headache Trends',
                'image': create_plot_base64(fig1)
            })

        # 2. Medications
        med_cols = [col for col in ['med1_mg', 'med2_mg', 'med3_mg', 'med4_mg'] if col in df.columns]
        if med_cols:
            fig2, ax2 = plt.subplots(figsize=(12,6))
            colors_bw = ['#000', '#333', '#666', '#999']
            markers = ['o', 's', '^', 'D']
            linestyles = ['-', '--', '-.', ':']
            for i, col in enumerate(med_cols):
                sns.lineplot(df, x='date', y=col, lw=2.5, label=f'Med {i+1}',
                           color=colors_bw[i], marker=markers[i], linestyle=linestyles[i], ax=ax2)
            ax2.set_title('Medication Dosages Over Time', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Date'); ax2.set_ylabel('Dosage (mg)')
            ax2.legend(); fig2.tight_layout()
            plots.append({
                'title': 'Medication Tracking',
                'image': create_plot_base64(fig2)
            })

        # 3. Headache vs Total Meds
        if 'headache_intensity' in df.columns and df['total_med_mg'].sum() > 0:
            fig3, ax3 = plt.subplots(figsize=(12,6))
            ax3_twin = ax3.twinx()
            sns.lineplot(df, x='date', y='headache_intensity', label='Headache',
                         color='#000', lw=2.5, marker='o', ax=ax3)
            sns.lineplot(df, x='date', y='total_med_mg', label='Total Medication',
                         color='#666', lw=2.5, ls='--', marker='s', ax=ax3_twin)
            ax3.set_title('Headache vs Total Medication', fontsize=14, fontweight='bold')
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Headache Intensity', color='#000')
            ax3_twin.set_ylabel('Total Medication (mg)', color='#666')
            ax3.legend(loc='upper left'); ax3_twin.legend(loc='upper right')
            fig3.tight_layout()
            plots.append({
                'title': 'Headache vs Medication Relationship',
                'image': create_plot_base64(fig3)
            })

        # 4. Energy, Appetite, Social (if available)
        wellness_cols = []
        if 'energy_level' in df.columns:
            wellness_cols.append(('energy_level', 'Energy', '#000', 'o', '-'))
        if 'appetite' in df.columns:
            wellness_cols.append(('appetite', 'Appetite', '#333', 's', '--'))
        if 'social_interaction' in df.columns:
            wellness_cols.append(('social_interaction', 'Social', '#666', '^', '-.'))

        if wellness_cols:
            fig4, ax4 = plt.subplots(figsize=(12,6))
            for col, label, color, marker, ls in wellness_cols:
                sns.lineplot(df, x='date', y=col, label=label, color=color, lw=2.5, marker=marker, linestyle=ls, ax=ax4)
            ax4.set_title('Wellness Metrics Over Time', fontsize=14, fontweight='bold')
            ax4.set_xlabel('Date'); ax4.set_ylabel('Score (1-10)')
            ax4.legend(); fig4.tight_layout()
            plots.append({
                'title': 'Wellness Tracking',
                'image': create_plot_base64(fig4)
            })

        # 5. Sleep Hours
        if 'sleep_hours' in df.columns:
            fig5, ax5 = plt.subplots(figsize=(12,6))
            sns.lineplot(df, x='date', y='sleep_hours', color='#000', lw=2.5, marker='o', ax=ax5)
            ax5.axhline(y=7, color='#666', linestyle='--', linewidth=2, label='Recommended (7h)')
            ax5.set_title('Sleep Pattern', fontsize=14, fontweight='bold')
            ax5.set_xlabel('Date'); ax5.set_ylabel('Hours')
            ax5.legend(); fig5.tight_layout()
            plots.append({
                'title': 'Sleep Tracking',
                'image': create_plot_base64(fig5)
            })

        # 6. Correlation Heatmap (for numeric columns)
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != 'total_med_mg']

        if len(numeric_cols) > 1:
            fig6, ax6 = plt.subplots(figsize=(10,8))
            corr = df[numeric_cols].corr()
            sns.heatmap(corr, annot=True, cmap='Greys', center=0, fmt='.2f', ax=ax6,
                        square=True, linewidths=2, linecolor='#000', cbar=True)
            ax6.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
            fig6.tight_layout()
            plots.append({
                'title': 'Correlation Analysis',
                'image': create_plot_base64(fig6)
            })

        # 7. Exercise tracking (if available)
        if 'exercise_minutes' in df.columns:
            fig7, ax7 = plt.subplots(figsize=(12,6))
            sns.barplot(df, x='date', y='exercise_minutes', color='#000', edgecolor='#000', linewidth=1.5, ax=ax7)
            ax7.set_title('Exercise Activity', fontsize=14, fontweight='bold')
            ax7.set_xlabel('Date'); ax7.set_ylabel('Minutes')
            plt.xticks(rotation=45)
            fig7.tight_layout()
            plots.append({
                'title': 'Exercise Log',
                'image': create_plot_base64(fig7)
            })

        # 8. Hope vs Mood (if available)
        if 'hope_score' in df.columns and 'mood_score' in df.columns:
            fig8, ax8 = plt.subplots(figsize=(12,6))
            sns.lineplot(df, x='date', y='mood_score', label='Mood', color='#000', lw=2.5, marker='o', ax=ax8)
            sns.lineplot(df, x='date', y='hope_score', label='Hope', color='#666', lw=2.5, marker='s', linestyle='--', ax=ax8)
            ax8.set_title('Mood vs Hope Score', fontsize=14, fontweight='bold')
            ax8.set_xlabel('Date'); ax8.set_ylabel('Score (1-10)')
            ax8.legend(); fig8.tight_layout()
            plots.append({
                'title': 'Emotional Well-being',
                'image': create_plot_base64(fig8)
            })

        # 9. Death Thoughts Tracking (if available)
        if 'die_thoughts' in df.columns:
            fig9, ax9 = plt.subplots(figsize=(12,6))
            sns.lineplot(df, x='date', y='die_thoughts', color='#000', lw=3, marker='o', markersize=8, ax=ax9)
            ax9.fill_between(df['date'], df['die_thoughts'], alpha=0.2, color='#000')
            ax9.set_title('Death Thoughts Intensity Over Time', fontsize=14, fontweight='bold')
            ax9.set_xlabel('Date'); ax9.set_ylabel('Intensity (0-10)')
            ax9.axhline(y=5, color='#666', linestyle='--', linewidth=1.5, alpha=0.5, label='Moderate Level')
            ax9.legend(); fig9.tight_layout()
            plots.append({
                'title': 'Death Thoughts Tracking',
                'image': create_plot_base64(fig9)
            })

        # 10. Custom numeric fields (auto-detect and graph)
        fields = load_fields_config()
        custom_numeric_fields = []
        predefined = ['mood_score', 'panic_intensity', 'headache_intensity', 'sleep_hours',
                      'hope_score', 'sedation_feeling', 'med1_mg', 'med2_mg', 'med3_mg', 'med4_mg',
                      'energy_level', 'appetite', 'social_interaction', 'exercise_minutes', 'die_thoughts']

        for field_name, field_config in fields.items():
            if field_name not in predefined and field_config['type'] == 'number' and field_name in df.columns:
                custom_numeric_fields.append((field_name, field_config['label']))

        if custom_numeric_fields:
            fig10, ax10 = plt.subplots(figsize=(12,6))
            for field_name, field_label in custom_numeric_fields:
                sns.lineplot(df, x='date', y=field_name, label=field_label, lw=2.5, marker='o', ax=ax10)
            ax10.set_title('Custom Metrics Over Time', fontsize=14, fontweight='bold')
            ax10.set_xlabel('Date'); ax10.set_ylabel('Value')
            ax10.legend(); fig10.tight_layout()
            plots.append({
                'title': 'Custom Fields Tracking',
                'image': create_plot_base64(fig10)
            })

        # Clear any remaining matplotlib figures to free memory
        plt.close('all')

        return render_template('graphs.html', plots=plots, entry_count=len(df))

    except Exception as e:
        plt.close('all')  # Clean up any figures
        flash(f'Error generating graphs: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/export-pdf')
def export_pdf():
    """Export complete report as PDF"""
    df = load_data()

    if df.empty:
        flash('No data to export!', 'warning')
        return redirect(url_for('index'))

    try:
        # Prepare data
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.sort_values('date')
        fields = load_fields_config()

        if df.empty:
            flash('No valid date entries found for export.', 'warning')
            return redirect(url_for('index'))

        # Create PDF
        pdf_filename = f'klinikum_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        # Use temp directory that works on both Windows and Unix
        import tempfile
        pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)

        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Center
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#37b24d'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        story.append(Paragraph("Medical Recovery Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
        story.append(Paragraph(f"Total Entries: {len(df)}", styles['Normal']))
        story.append(Paragraph(f"Date Range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Note to Readers
        note_style = ParagraphStyle(
            'NoteStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            leftIndent=20,
            rightIndent=20,
            alignment=4  # Justify
        )

        note_title_style = ParagraphStyle(
            'NoteTitleStyle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

        story.append(Paragraph("Note to Readers", note_title_style))
        story.append(Paragraph(
            "This data is subjective and reflects how I felt. This report is a personal and analytical reflection on my time in the Klinikum. "
            "It combines information drawn from memory, journals, WhatsApp conversations, and available medical data to trace the patterns of my mental state during recovery.",
            note_style
        ))
        story.append(Paragraph(
            "The intention behind this work is not to diagnose or justify, but to understand — to recognize how sleep, medication, thought patterns, and emotional changes interacted across days and weeks.",
            note_style
        ))
        story.append(Paragraph(
            "While I have taken care to ensure the accuracy of data and interpretation, this report remains deeply personal and subjective in nature. "
            "Some parts were reconstructed retrospectively and may not perfectly represent medical reality, but they reflect my lived experience as faithfully as possible.",
            note_style
        ))
        story.append(Paragraph(
            "Readers are encouraged to approach this document with empathy and respect, keeping in mind that mental health is complex, non-linear, and often resistant to tidy explanations. "
            "What follows is not just data — it's the story of a mind learning to make sense of itself.",
            note_style
        ))
        story.append(Spacer(1, 0.3*inch))

        # Summary Statistics
        story.append(Paragraph("Summary Statistics", heading_style))

        summary_data = [['Metric', 'Average', 'Min', 'Max']]
        for field_name, field_config in fields.items():
            if field_config['type'] == 'number' and field_name in df.columns:
                col_data = pd.to_numeric(df[field_name], errors='coerce')
                if not col_data.isna().all():
                    summary_data.append([
                        field_config['label'],
                        f"{col_data.mean():.1f}",
                        f"{col_data.min():.0f}",
                        f"{col_data.max():.0f}"
                    ])

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37b24d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(PageBreak())

        # Generate and add graphs
        story.append(Paragraph("Visualizations", heading_style))
        story.append(Spacer(1, 0.2*inch))

        # Calculate total_med_mg for graphs
        df['total_med_mg'] = 0
        for col in ['med1_mg', 'med2_mg', 'med3_mg', 'med4_mg']:
            if col in df.columns:
                df['total_med_mg'] += pd.to_numeric(df[col], errors='coerce').fillna(0)

        sns.set_theme(style="whitegrid",
                      rc={"axes.facecolor":"#ffffff",
                          "grid.color":"#cccccc",
                          "axes.edgecolor":"#000000",
                          "axes.linewidth":2,
                          "grid.linewidth":0.5,
                          "font.family":"monospace"})

        # Graph 1: Mood/Panic/Headache
        if all(col in df.columns for col in ['mood_score', 'panic_intensity', 'headache_intensity']):
            fig, ax = plt.subplots(figsize=(7,4))
            sns.lineplot(df, x='date', y='mood_score', label='Mood', color='#000', lw=2, marker='o', ax=ax)
            sns.lineplot(df, x='date', y='panic_intensity', label='Panic', color='#000', lw=2, ls='--', marker='s', ax=ax)
            sns.lineplot(df, x='date', y='headache_intensity', label='Headache', color='#666', lw=2, ls=':', marker='^', ax=ax)
            ax.set_title('Core Symptoms', fontweight='bold')
            ax.legend()
            fig.tight_layout()

            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            story.append(RLImage(img_buffer, width=6*inch, height=3.5*inch))
            plt.close(fig)
            story.append(Spacer(1, 0.2*inch))

        # Graph 2: Sleep
        if 'sleep_hours' in df.columns:
            fig, ax = plt.subplots(figsize=(7,4))
            sns.lineplot(df, x='date', y='sleep_hours', color='#000', lw=2, marker='o', ax=ax)
            ax.axhline(y=7, color='#666', linestyle='--', linewidth=2, label='Recommended')
            ax.set_title('Sleep Pattern', fontweight='bold')
            ax.legend()
            fig.tight_layout()

            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            story.append(RLImage(img_buffer, width=6*inch, height=3.5*inch))
            plt.close(fig)
            story.append(PageBreak())

        # Daily Notes
        story.append(Paragraph("Daily Notes", heading_style))
        story.append(Spacer(1, 0.1*inch))

        for _, row in df.iterrows():
            date_str = row['date'].strftime('%B %d, %Y')
            note_text = str(row.get('notes', 'No notes'))

            story.append(Paragraph(f"<b>{date_str}</b>", styles['Normal']))
            story.append(Paragraph(note_text, styles['Normal']))
            story.append(Spacer(1, 0.15*inch))

        # Footer
        story.append(PageBreak())
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=1  # Center
        )
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph("Generated with care and introspection", footer_style))
        story.append(Paragraph(f"Data period: {df['date'].min().strftime('%B %Y')} - {df['date'].max().strftime('%B %Y')}", footer_style))
        # Uncomment and modify the line below to add a link
        # story.append(Paragraph('<link href="https://your-website.com">Additional Resources</link>', footer_style))

        # Build PDF
        doc.build(story)

        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')

    except Exception as e:
        plt.close('all')  # Clean up any figures
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize fields config if it doesn't exist
    if not os.path.exists(FIELDS_CONFIG_FILE):
        save_fields_config(DEFAULT_FIELDS)

    app.run(debug=True, port=5000)
