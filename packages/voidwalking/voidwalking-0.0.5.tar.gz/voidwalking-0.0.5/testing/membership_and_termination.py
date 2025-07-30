import torch
from voidwalker import Voidwalker
import pandas as pd
import numpy as np

# Set random seed and bounds
torch.manual_seed(42)
WINDOW = torch.tensor([[-500., 500.],
                       [-500., 500.]],
                      dtype=torch.float32)

# Load MINFLUX measurement data
data_prefix = 'Nup96_sparse'
file_path = f'/Users/jackpeyton/LocalDocs/groupa_data/outputs/{data_prefix}_gra_seed_0_JACKSIM_infomap_S_5.0nm_sigma_BF1.0_rollingball-1.0nm/CLUSTERING_RESULTS_clustered_results_2d.csv'
df = pd.read_csv(file_path)
emitter_pos = df[["x", "y"]].to_numpy()
X = torch.tensor(emitter_pos, dtype=torch.float32)

# Run Voidwalker with frame recording
vw = Voidwalker(
    X,
    n_samples=5_000,
    n_voids=250,
    margin=10,
    growth_step=0.2,
    max_radius=100,
    initial_radius=10,
    move_step=0.5,
    max_steps=5_000,
    max_failures=50,
    outer_ring_width=20,
    alpha=0.05,
    record_frames=False
)

voids, radii, _ = vw.run()

print(vw.termination_reason)

for i, members in enumerate(vw.memberships):
    print(f"Void {i}: {len(members)} points -> {members.tolist()}")

all_members = torch.cat([m for m in vw.memberships if len(m) > 0])
unique_members = torch.unique(all_members)
print(f"Total unique member points: {len(unique_members)}")

import matplotlib.pyplot as plt

# Plot Y points
plt.figure(figsize=(8, 8))
plt.scatter(X[:, 0], X[:, 1], s=5, alpha=0.5, label='Points')

# Plot voids with colour based on termination reason
centres = voids[:, :2]
radii = radii.numpy()
termination = vw.termination_reason.numpy()

for centre, radius, reason in zip(centres, radii, termination):
    colour = 'blue' if reason == 0 else 'black'
    circle = plt.Circle(centre, radius, fill=False, linewidth=1.5, edgecolor=colour)
    plt.gca().add_patch(circle)

plt.title("MINFLUX Points and Final Voids (Blue = CSR Termination)")
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.legend()
plt.show()

# Identify non-member points
all_indices = torch.arange(X.shape[0])
non_members = torch.tensor([i for i in all_indices if i not in unique_members])

plt.figure(figsize=(8, 8))
plt.scatter(X[non_members, 0], X[non_members, 1], s=5, c='red', alpha=0.6, label='Non-member points')
plt.scatter(X[unique_members, 0], X[unique_members, 1], s=5, c='blue', alpha=0.6, label='Member points')

# Plot voids
for centre, radius, reason in zip(centres, radii, termination):
    colour = 'blue' if reason == 0 else 'black'
    circle = plt.Circle(centre, radius, fill=False, linewidth=1.5, edgecolor=colour)
    plt.gca().add_patch(circle)

plt.title("MINFLUX Points: Red = Unexplained, Blue = Members, Circles = Voids")
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.legend()
plt.show()