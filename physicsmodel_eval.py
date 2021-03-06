from PhysicsModel import PhysicsModel
from data_loader import TestSet
import numpy as np
from torch.utils.data import DataLoader

# physicsmodel_eval.py:	Evaluate physics-based robotic system predictive models over multiple steps


def mse_loss(x1, x2):
    # Returns the mean square error loss for two nx1 vectors
    e = np.abs(x1-x2)
    n = x1.shape[0]
    return np.dot(e.T, e)/n


if __name__ == "__main__":
    # Simulation Model Parameters
    l = 0.211  # length (m)
    d = 1.7e-5  # blade parameter
    m = 1  # mass (kg)
    kt = 2.35e-14  # translational drag coefficient
    kr = 0.0099  # rotational drag coefficient
    ixx = 0.002  # moment of inertia about X-axis
    iyy = 0.002  # moment of inertia about Y-axis
    izz = 0.001  # moment of inertia about Z-axis

    # Define training/validation datasets and dataloaders
    P = 1
    F = 90
    test_set = TestSet('data/AscTec_Pelican_Flight_Dataset.mat', P, F, full_state=True)
    test_loader = DataLoader(test_set, batch_size=1, shuffle=True, num_workers=0)

    i = 0
    vel_losses = np.zeros((len(test_set), F))
    rate_losses = np.zeros((len(test_set), F))

    for data in test_loader:
        input = data["input"][:, 0, :].numpy().T    # Load previous state for prediction
        model = PhysicsModel(l, d, m, kt, kr, ixx, iyy, izz, init_state=input[:12, :])  # Initialize physics-based model

        for j in range(F):
            label = data["label"][:, j, :].numpy().T    # Load label

            # Forward simulation
            model.update_thrust(label[12:, :])
            model.update_torques()
            model.update(0.01)

            # Calculate losses
            vel_loss = mse_loss(model.vel, label[9:12, :])
            rate_loss = mse_loss(model.rate, label[6:9, :])
            vel_losses[i][j] = vel_loss
            rate_losses[i][j] = rate_loss

        i += 1
        if i % 100 == 0:
            print("Iteration: {}".format(i))

    np.savetxt("WB_test_error_rates.csv", rate_losses)
    np.savetxt("WB_test_error_vels.csv", vel_losses)

