from utils.simulation_manager import HospitalSimulator
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_hospital(hospital_simulator, current_time):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    
    # ED Visualization (left side)
    ax1.set_title(f'Emergency Department\nTime: {current_time}')
    ed_patients = hospital_simulator.ed.patients
    for i, patient in enumerate(ed_patients):
        y = len(ed_patients) - i  # Stack patients from bottom to top
        rect = patches.Rectangle((0.1, y-0.8), 0.8, 0.6, facecolor='lightblue')
        ax1.add_patch(rect)
        ax1.text(0.15, y-0.6, f"ID:{patient.id} - {patient.name}", fontsize=9)
        ax1.text(0.15, y-0.4, f"→ {patient.destination_loc}", fontsize=9)
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, max(10, len(ed_patients) + 1))
    
    # Wards Visualization (right side)
    ax2.set_title('Wards')
    total_y = 0
    colors = {'ICU': 'lightcoral', 'CCU': 'lightgreen', 'AMU': 'lightyellow',
              'SSU': 'lightgray', 'SW': 'lightpink'}
    
    # Calculate max patients for spacing
    max_patients = max(len(ward.patients) for ward in hospital_simulator.wards_dict.values())
    spacing = max(3, max_patients) * 2  # Increased spacing between wards
    
    for ward_name, ward in hospital_simulator.wards_dict.items():
        # Draw ward separator and name
        ax2.axhline(y=total_y, color='black', linestyle='-', linewidth=1)
        ax2.text(0.02, total_y + spacing/2, ward_name, fontsize=12, fontweight='bold')
        
        # Draw patients in ward
        for i, patient in enumerate(ward.patients):
            y_pos = total_y + spacing - (i * 2)  # More space between patients
            rect = patches.Rectangle((0.2, y_pos-0.4), 0.6, 0.8,
                                  facecolor=colors.get(ward_name, 'lightgray'))
            ax2.add_patch(rect)
            
            # Patient ID and name on one line, destination on separate line below
            id_text = f"ID:{patient.id} - {patient.name}"
            dest_text = f"→ {patient.destination_loc}"
            
            # Calculate text position to right-align ID
            id_x = 0.85 - len(id_text) * 0.01  # Adjust multiplier as needed
            ax2.text(id_x, y_pos-0.15, id_text, fontsize=9)
            ax2.text(0.25, y_pos-0.15, dest_text, fontsize=9)
        
        total_y += spacing + 2  # Added more padding between wards
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, max(total_y, 70))  # Ensure minimum height for visibility
    
    plt.tight_layout()
    plt.show()

# Main simulation setup
start_time = "2025-09-21 17:00:00"
hospital_simulator = HospitalSimulator(1, 10, start_time=start_time)
current_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

print('Initial ED patients:', hospital_simulator.ed.patients)
print('Press q to close plot and advance to next time step')

while True:
    print(f'--------------------------------')
    print(f'Time: {current_time}')
    hospital_simulator.run_simulation_step(current_time)
    visualize_hospital(hospital_simulator, current_time)
    current_time += datetime.timedelta(minutes=10)