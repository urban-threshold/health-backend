from utils.simulation_manager import HospitalSimulator
import datetime
from utils.triage_levels import get_triage_level
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_hospital(hospital_simulator, current_time, auto_close_time=None):
    plt.clf()  # Clear any existing plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    
    # ED Visualization (left side)
    ax1.set_title(f'Emergency Department\nTime: {current_time}')
    ed_patients = hospital_simulator.ed.patients
    ed_capacity = hospital_simulator.ed.capacity
    
    # Show all ED beds, including empty ones
    for i in range(ed_capacity):
        y = ed_capacity - i  # Stack from bottom to top
        # Draw empty bed as black line
        rect = patches.Rectangle((0.1, y-0.8), 0.8, 0.1, facecolor='black', alpha=0.1)
        ax1.add_patch(rect)
    
    # Draw occupied ED beds
    for i, patient in enumerate(ed_patients):
        y = ed_capacity - i
        rect = patches.Rectangle((0.1, y-0.8), 0.8, 0.8, facecolor='lightblue')  # Made taller for more text
        ax1.add_patch(rect)
        triage = get_triage_level(patient.triage_level_desc)
        # Format times without microseconds
        arrival = patient.ED_arrival_time.strftime("%H:%M:%S")
        exit_time = patient.ED_exit_time.strftime("%H:%M:%S") if patient.ED_exit_time else "TBD"
        
        ax1.text(0.15, y-0.4, f"ID:{patient.id} - {patient.name} (T{triage})", fontsize=9)
        ax1.text(0.15, y-0.6, f"→ {patient.destination_loc}", fontsize=9)
        ax1.text(0.15, y-0.75, f"Arrival: {arrival} → Exit: {exit_time}", fontsize=8)
    
    ax1.text(0.02, ed_capacity + 0.5, f"Beds: {len(ed_patients)}/{ed_capacity}", 
             fontsize=10, fontweight='bold')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, max(10, ed_capacity + 1))
    
    # Wards Visualization (right side)
    ax2.set_title('Wards')
    total_y = 0
    colors = {'ICU': 'lightcoral', 'CCU': 'lightgreen', 'AMU': 'lightyellow',
              'SSU': 'lightgray', 'SW': 'lightpink'}
    
    # Calculate spacing based on maximum ward capacity
    max_capacity = max(ward.capacity for ward in hospital_simulator.wards_dict.values())
    spacing = max(3, max_capacity) * 2  # Increased spacing between wards
    
    for ward_name, ward in hospital_simulator.wards_dict.items():
        # Draw ward separator and name
        ax2.axhline(y=total_y, color='black', linestyle='-', linewidth=1)
        ax2.text(0.02, total_y + spacing/2, f"{ward_name}\nBeds: {len(ward.patients)}/{ward.capacity}", 
                fontsize=10, fontweight='bold')
        
        # Draw all beds, including empty ones
        for i in range(ward.capacity):
            y_pos = total_y + spacing - (i * 2)
            # Draw empty bed as black line
            rect = patches.Rectangle((0.2, y_pos-0.1), 0.6, 0.1, 
                                  facecolor='black', alpha=0.1)
            ax2.add_patch(rect)
        
        # Draw occupied beds with patients
        for i, patient in enumerate(ward.patients):
            y_pos = total_y + spacing - (i * 2)
            rect = patches.Rectangle((0.2, y_pos-0.4), 0.6, 0.8,
                                  facecolor=colors.get(ward_name, 'lightgray'))
            ax2.add_patch(rect)
            
            # Add triage level to patient info
            triage = get_triage_level(patient.triage_level_desc)
            id_text = f"ID:{patient.id} - {patient.name} (T{triage})"
            dest_text = f"→ {patient.destination_loc}"
            
            # Calculate text position to right-align ID
            id_x = 0.85 - len(id_text) * 0.01
            ax2.text(id_x, y_pos-0.15, id_text, fontsize=9)
            ax2.text(0.25, y_pos-0.15, dest_text, fontsize=9)
        
        total_y += spacing + 2
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, max(total_y, 70))
    
    plt.tight_layout()
    
    if auto_close_time:
        plt.pause(auto_close_time)
        plt.close(fig)
    else:
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
    visualize_hospital(hospital_simulator, current_time, auto_close_time=1)  # Auto-close after 1 second
    current_time += datetime.timedelta(minutes=10)