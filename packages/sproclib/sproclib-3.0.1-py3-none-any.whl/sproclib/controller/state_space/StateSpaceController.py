"""
State-Space Controller for SPROCLIB - Standard Process Control Library

This module implements state-space control methods using direct control
with state-space model representation (A, B, C, D matrices).

Applications:
- Reactor networks with multiple interconnected units
- Coupled process units (heat integration, mass integration)
- MIMO (Multiple Input Multiple Output) systems
- Advanced control of complex chemical processes

Author: Thorsten Gressling <gressling@paramus.ai>
License: MIT License
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List, Union
import logging
from abc import ABC, abstractmethod
from scipy.linalg import solve_continuous_are, inv, eigvals, solve_lyapunov
from scipy.signal import place_poles

logger = logging.getLogger(__name__)


class StateSpaceModel:
    """
    State-space model representation for control design.
    
    Represents a linear time-invariant system:
    dx/dt = A*x + B*u + E*d
    y = C*x + D*u + F*d
    
    Where:
    - x: state vector
    - u: input vector (manipulated variables)
    - d: disturbance vector
    - y: output vector (measured variables)
    """
    
    def __init__(
        self,
        A: np.ndarray,
        B: np.ndarray,
        C: np.ndarray,
        D: Optional[np.ndarray] = None,
        E: Optional[np.ndarray] = None,
        F: Optional[np.ndarray] = None,
        state_names: Optional[List[str]] = None,
        input_names: Optional[List[str]] = None,
        output_names: Optional[List[str]] = None,
        name: str = "StateSpaceModel"
    ):
        """
        Initialize state-space model.
        
        Args:
            A: State matrix [n_states x n_states]
            B: Input matrix [n_states x n_inputs]
            C: Output matrix [n_outputs x n_states]
            D: Feedthrough matrix [n_outputs x n_inputs] (optional)
            E: Disturbance state matrix [n_states x n_disturbances] (optional)
            F: Disturbance output matrix [n_outputs x n_disturbances] (optional)
            state_names: Names of state variables
            input_names: Names of input variables
            output_names: Names of output variables
            name: Model name
        """
        self.A = np.asarray(A)
        self.B = np.asarray(B)
        self.C = np.asarray(C)
        self.name = name
        
        # Validate dimensions
        self.n_states = self.A.shape[0]
        self.n_inputs = self.B.shape[1]
        self.n_outputs = self.C.shape[0]
        
        if self.A.shape != (self.n_states, self.n_states):
            raise ValueError(f"A matrix must be {self.n_states}x{self.n_states}")
        if self.B.shape != (self.n_states, self.n_inputs):
            raise ValueError(f"B matrix must be {self.n_states}x{self.n_inputs}")
        if self.C.shape != (self.n_outputs, self.n_states):
            raise ValueError(f"C matrix must be {self.n_outputs}x{self.n_states}")
        
        # Optional matrices
        if D is not None:
            self.D = np.asarray(D)
            if self.D.shape != (self.n_outputs, self.n_inputs):
                raise ValueError(f"D matrix must be {self.n_outputs}x{self.n_inputs}")
        else:
            self.D = np.zeros((self.n_outputs, self.n_inputs))
        
        if E is not None:
            self.E = np.asarray(E)
            self.n_disturbances = self.E.shape[1]
            if self.E.shape[0] != self.n_states:
                raise ValueError(f"E matrix must have {self.n_states} rows")
        else:
            self.E = None
            self.n_disturbances = 0
        
        if F is not None:
            self.F = np.asarray(F)
            if self.E is None:
                raise ValueError("E matrix must be provided if F matrix is given")
            if self.F.shape != (self.n_outputs, self.n_disturbances):
                raise ValueError(f"F matrix must be {self.n_outputs}x{self.n_disturbances}")
        else:
            self.F = np.zeros((self.n_outputs, self.n_disturbances)) if self.E is not None else None
        
        # Variable names
        self.state_names = state_names or [f"x{i+1}" for i in range(self.n_states)]
        self.input_names = input_names or [f"u{i+1}" for i in range(self.n_inputs)]
        self.output_names = output_names or [f"y{i+1}" for i in range(self.n_outputs)]
        
        logger.info(f"StateSpaceModel '{name}' initialized: {self.n_states} states, "
                   f"{self.n_inputs} inputs, {self.n_outputs} outputs")
    
    def simulate(
        self,
        t: np.ndarray,
        u: np.ndarray,
        x0: np.ndarray,
        d: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate state-space model response.
        
        Args:
            t: Time array
            u: Input array [len(t) x n_inputs]
            x0: Initial state [n_states]
            d: Disturbance array [len(t) x n_disturbances] (optional)
            
        Returns:
            Tuple of (states, outputs) arrays
        """
        from scipy.integrate import solve_ivp
        
        if u.shape != (len(t), self.n_inputs):
            raise ValueError(f"Input array must be {len(t)}x{self.n_inputs}")
        
        if d is not None and self.E is not None:
            if d.shape != (len(t), self.n_disturbances):
                raise ValueError(f"Disturbance array must be {len(t)}x{self.n_disturbances}")
        
        def dynamics(time, x):
            # Interpolate inputs at current time
            t_idx = np.searchsorted(t, time)
            t_idx = min(t_idx, len(t) - 1)
            
            u_current = u[t_idx, :]
            d_current = d[t_idx, :] if d is not None and self.E is not None else np.zeros(self.n_disturbances)
            
            # State dynamics: dx/dt = A*x + B*u + E*d
            dxdt = self.A @ x + self.B @ u_current
            if self.E is not None:
                dxdt += self.E @ d_current
            
            return dxdt
        
        # Solve ODE
        sol = solve_ivp(dynamics, [t[0], t[-1]], x0, t_eval=t, dense_output=True)
        
        if not sol.success:
            raise RuntimeError("State-space simulation failed")
        
        states = sol.y.T  # [len(t) x n_states]
        
        # Calculate outputs: y = C*x + D*u + F*d
        outputs = np.zeros((len(t), self.n_outputs))
        for i in range(len(t)):
            outputs[i, :] = self.C @ states[i, :] + self.D @ u[i, :]
            if d is not None and self.F is not None:
                outputs[i, :] += self.F @ d[i, :]
        
        return states, outputs
    
    def step_response(
        self,
        t: np.ndarray,
        input_index: int = 0,
        step_magnitude: float = 1.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate step response for specified input.
        
        Args:
            t: Time array
            input_index: Index of input for step test
            step_magnitude: Magnitude of step input
            
        Returns:
            Tuple of (states, outputs) arrays
        """
        u = np.zeros((len(t), self.n_inputs))
        u[:, input_index] = step_magnitude
        
        x0 = np.zeros(self.n_states)
        
        return self.simulate(t, u, x0)
    
    def controllability_matrix(self) -> np.ndarray:
        """Calculate controllability matrix [B AB A²B ... A^(n-1)B]"""
        P = np.zeros((self.n_states, self.n_states * self.n_inputs))
        A_power = np.eye(self.n_states)
        
        for i in range(self.n_states):
            start_col = i * self.n_inputs
            end_col = (i + 1) * self.n_inputs
            P[:, start_col:end_col] = A_power @ self.B
            A_power = A_power @ self.A
        
        return P
    
    def observability_matrix(self) -> np.ndarray:
        """Calculate observability matrix [C; CA; CA²; ...; CA^(n-1)]"""
        O = np.zeros((self.n_states * self.n_outputs, self.n_states))
        A_power = np.eye(self.n_states)
        
        for i in range(self.n_states):
            start_row = i * self.n_outputs
            end_row = (i + 1) * self.n_outputs
            O[start_row:end_row, :] = self.C @ A_power
            A_power = A_power @ self.A
        
        return O
    
    def is_controllable(self) -> bool:
        """Check if system is controllable"""
        P = self.controllability_matrix()
        rank_P = np.linalg.matrix_rank(P)
        return rank_P == self.n_states
    
    def is_observable(self) -> bool:
        """Check if system is observable"""
        O = self.observability_matrix()
        rank_O = np.linalg.matrix_rank(O)
        return rank_O == self.n_states
    
    def is_stable(self) -> bool:
        """Check if system is stable (all eigenvalues have negative real parts)"""
        eigenvalues = eigvals(self.A)
        return np.all(np.real(eigenvalues) < 0)
    
    def poles(self) -> np.ndarray:
        """Get system poles (eigenvalues of A matrix)"""
        return eigvals(self.A)
    
    def zeros(self) -> np.ndarray:
        """Calculate system zeros (transmission zeros)"""
        # For MIMO systems, this is more complex
        # This is a simplified calculation for square systems
        if self.n_inputs != self.n_outputs:
            logger.warning("Zero calculation implemented only for square systems")
            return np.array([])
        
        try:
            # Rosenbrock system matrix
            s = 1j * np.logspace(-2, 2, 1000)  # Frequency range for search
            zeros = []
            
            for si in s:
                P = np.block([
                    [si * np.eye(self.n_states) - self.A, -self.B],
                    [self.C, self.D]
                ])
                if np.linalg.matrix_rank(P) < (self.n_states + self.n_inputs):
                    zeros.append(si)
            
            return np.array(zeros)
        except:
            return np.array([])
    
    def describe(self) -> Dict[str, Any]:
        """
        Comprehensive description of the State-Space Model.
        
        Returns:
            Dictionary containing detailed information about state-space
            representation, system properties, and analysis results.
        """
        return {
            'class_name': 'StateSpaceModel',
            'model_name': self.name,
            'description': 'Linear time-invariant state-space model representation',
            'purpose': 'Mathematical representation of dynamic systems for control design',
            
            'system_dimensions': {
                'states': self.n_states,
                'inputs': self.n_inputs, 
                'outputs': self.n_outputs,
                'disturbances': self.n_disturbances
            },
            
            'variable_names': {
                'states': self.state_names,
                'inputs': self.input_names,
                'outputs': self.output_names
            },
            
            'mathematical_representation': {
                'state_equation': 'dx/dt = A*x + B*u + E*d',
                'output_equation': 'y = C*x + D*u + F*d',
                'matrix_meanings': {
                    'A': f'State matrix [{self.n_states}x{self.n_states}] - internal dynamics',
                    'B': f'Input matrix [{self.n_states}x{self.n_inputs}] - input coupling',
                    'C': f'Output matrix [{self.n_outputs}x{self.n_states}] - measurement equation',
                    'D': f'Feedthrough matrix [{self.n_outputs}x{self.n_inputs}] - direct coupling',
                    'E': f'Disturbance state matrix [{self.n_states}x{self.n_disturbances}] - disturbance effects on states' if self.E is not None else 'Not specified',
                    'F': f'Disturbance output matrix [{self.n_outputs}x{self.n_disturbances}] - disturbance effects on outputs' if self.F is not None else 'Not specified'
                }
            },
            
            'system_properties': {
                'controllability': self.is_controllable(),
                'observability': self.is_observable(),
                'stability': self.is_stable(),
                'poles': self.poles().tolist(),
                'has_disturbances': self.E is not None,
                'has_feedthrough': not np.allclose(self.D, 0),
                'system_type': self._classify_system_type()
            },
            
            'control_system_theory': {
                'controllability_definition': 'All states can be controlled by the inputs',
                'observability_definition': 'All states can be determined from the outputs',
                'stability_definition': 'All eigenvalues have negative real parts',
                'pole_significance': 'Eigenvalues determine natural response characteristics',
                'design_implications': {
                    'controllable_not_observable': 'Can control but cannot fully estimate states',
                    'observable_not_controllable': 'Can estimate but cannot fully control states',
                    'both_controllable_observable': 'Ideal for state-space control design',
                    'neither': 'System may need decomposition or redesign'
                }
            },
            
            'chemical_engineering_context': {
                'typical_states': [
                    'Concentrations of chemical species',
                    'Temperature profiles in reactors/columns',
                    'Pressure levels in vessels',
                    'Liquid levels in tanks',
                    'Flow rates in recycle streams'
                ],
                'typical_inputs': [
                    'Feed flow rates',
                    'Coolant/heating medium flows',
                    'Valve positions',
                    'Catalyst addition rates',
                    'Utility consumption rates'
                ],
                'typical_outputs': [
                    'Product concentrations',
                    'Temperature measurements',
                    'Pressure readings',
                    'Level indicators',
                    'Quality measurements'
                ],
                'common_applications': [
                    'Continuous stirred tank reactors (CSTR)',
                    'Distillation column dynamics',
                    'Heat exchanger networks',
                    'Reactor-separator systems',
                    'Crystallization processes'
                ]
            },
            
            'model_validation': {
                'matrix_conditioning': {
                    'A_condition_number': float(np.linalg.cond(self.A)),
                    'controllability_matrix_rank': np.linalg.matrix_rank(self.controllability_matrix()),
                    'observability_matrix_rank': np.linalg.matrix_rank(self.observability_matrix())
                },
                'physical_constraints': {
                    'check_units': 'Verify consistent units across all matrices',
                    'check_signs': 'Validate sign conventions for physical processes',
                    'check_magnitudes': 'Ensure realistic parameter values'
                }
            },
            
            'simulation_capabilities': {
                'available_methods': [
                    'Time domain simulation with initial conditions',
                    'Step response analysis',
                    'Impulse response calculation',
                    'Frequency response evaluation'
                ],
                'input_requirements': {
                    'initial_states': f'Vector of length {self.n_states}',
                    'input_signals': f'Array of shape [time_points, {self.n_inputs}]',
                    'disturbances': f'Array of shape [time_points, {self.n_disturbances}]' if self.E is not None else 'Not applicable'
                }
            },
            
            'analysis_tools': {
                'available_methods': [
                    'poles() - System eigenvalues',
                    'zeros() - Transmission zeros', 
                    'is_stable() - Stability check',
                    'is_controllable() - Controllability test',
                    'is_observable() - Observability test',
                    'simulate() - Time domain simulation'
                ]
            }
        }
    
    def _classify_system_type(self) -> str:
        """Classify the type of system based on properties."""
        if self.n_inputs == 1 and self.n_outputs == 1:
            system_type = "SISO (Single Input Single Output)"
        elif self.n_inputs > 1 and self.n_outputs > 1:
            system_type = "MIMO (Multiple Input Multiple Output)"
        elif self.n_inputs == 1 and self.n_outputs > 1:
            system_type = "SIMO (Single Input Multiple Output)"
        else:
            system_type = "MISO (Multiple Input Single Output)"
        
        if not self.is_stable():
            system_type += " - Unstable"
        else:
            system_type += " - Stable"
            
        return system_type


class StateSpaceController:
    """
    State-Space Controller using full state feedback.
    
    Implements various state-space control methods:
    - Pole placement
    - Linear Quadratic Regulator (LQR)
    - State observer design
    """
    
    def __init__(
        self,
        model: StateSpaceModel,
        control_method: str = "lqr",
        name: str = "StateSpaceController"
    ):
        """
        Initialize state-space controller.
        
        Args:
            model: State-space model
            control_method: Control method ('pole_placement', 'lqr')
            name: Controller name
        """
        self.model = model
        self.control_method = control_method
        self.name = name
        
        # Controller matrices
        self.K = None  # State feedback gain matrix
        self.L = None  # Observer gain matrix
        self.N = None  # Reference tracking matrix
        
        # Controller state
        self.x_hat = np.zeros(model.n_states)  # State estimate
        self.integral_states = np.zeros(model.n_outputs)  # Integral states for tracking
        self.last_update_time = None
        
        # Validate controllability and observability
        if not model.is_controllable():
            logger.warning(f"System is not fully controllable")
        if not model.is_observable():
            logger.warning(f"System is not fully observable")
        
        logger.info(f"StateSpaceController '{name}' initialized using {control_method}")
    
    def design_lqr_controller(
        self,
        Q: np.ndarray,
        R: np.ndarray,
        N: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Design Linear Quadratic Regulator (LQR) controller.
        
        Minimizes cost function: J = ∫(x'Qx + u'Ru + 2x'Nu) dt
        
        Args:
            Q: State weighting matrix [n_states x n_states]
            R: Input weighting matrix [n_inputs x n_inputs]
            N: Cross-weighting matrix [n_states x n_inputs] (optional)
            
        Returns:
            State feedback gain matrix K
        """
        if Q.shape != (self.model.n_states, self.model.n_states):
            raise ValueError(f"Q matrix must be {self.model.n_states}x{self.model.n_states}")
        if R.shape != (self.model.n_inputs, self.model.n_inputs):
            raise ValueError(f"R matrix must be {self.model.n_inputs}x{self.model.n_inputs}")
        
        if N is None:
            N = np.zeros((self.model.n_states, self.model.n_inputs))
        elif N.shape != (self.model.n_states, self.model.n_inputs):
            raise ValueError(f"N matrix must be {self.model.n_states}x{self.model.n_inputs}")
        
        # Solve Algebraic Riccati Equation (ARE)
        try:
            P = solve_continuous_are(self.model.A, self.model.B, Q, R, e=None, s=None)
            
            # Calculate optimal gain: K = R^(-1) * (B'P + N')
            R_inv = inv(R)
            self.K = R_inv @ (self.model.B.T @ P + N.T)
            
            # Check closed-loop stability
            A_cl = self.model.A - self.model.B @ self.K
            if not np.all(np.real(eigvals(A_cl)) < 0):
                logger.warning("LQR controller may be unstable")
            
            logger.info(f"LQR controller designed with closed-loop poles: {eigvals(A_cl)}")
            return self.K
            
        except Exception as e:
            raise RuntimeError(f"LQR design failed: {e}")
    
    def design_pole_placement_controller(
        self,
        desired_poles: np.ndarray
    ) -> np.ndarray:
        """
        Design controller using pole placement.
        
        Args:
            desired_poles: Desired closed-loop poles
            
        Returns:
            State feedback gain matrix K
        """
        if len(desired_poles) != self.model.n_states:
            raise ValueError(f"Must specify {self.model.n_states} poles")
        
        # Check if all poles have negative real parts
        if not np.all(np.real(desired_poles) < 0):
            logger.warning("Some desired poles have non-negative real parts")
        
        try:
            # Use scipy's pole placement
            result = place_poles(self.model.A, self.model.B, desired_poles)
            self.K = result.gain_matrix
            
            logger.info(f"Pole placement controller designed")
            logger.info(f"Achieved poles: {result.computed_poles}")
            return self.K
            
        except Exception as e:
            raise RuntimeError(f"Pole placement failed: {e}")
    
    def design_observer(
        self,
        observer_poles: np.ndarray,
        method: str = "pole_placement"
    ) -> np.ndarray:
        """
        Design state observer (Luenberger observer).
        
        Args:
            observer_poles: Desired observer poles
            method: Observer design method ('pole_placement', 'lqr')
            
        Returns:
            Observer gain matrix L
        """
        if len(observer_poles) != self.model.n_states:
            raise ValueError(f"Must specify {self.model.n_states} observer poles")
        
        # Observer poles should be faster than controller poles
        if not np.all(np.real(observer_poles) < 0):
            logger.warning("Some observer poles have non-negative real parts")
        
        try:
            if method == "pole_placement":
                # Dual problem: place poles of (A-LC)'
                result = place_poles(self.model.A.T, self.model.C.T, observer_poles)
                self.L = result.gain_matrix.T
            else:
                raise ValueError(f"Unknown observer design method: {method}")
            
            # Verify observer stability
            A_obs = self.model.A - self.L @ self.model.C
            obs_poles = eigvals(A_obs)
            logger.info(f"Observer designed with poles: {obs_poles}")
            
            return self.L
            
        except Exception as e:
            raise RuntimeError(f"Observer design failed: {e}")
    
    def design_reference_tracking(self) -> np.ndarray:
        """
        Design reference tracking for step inputs.
        
        Calculates feedforward gain N such that steady-state error is zero.
        
        Returns:
            Reference tracking matrix N
        """
        try:
            # For step reference tracking: N = -[C(A-BK)^(-1)B]^(-1)
            A_cl = self.model.A - self.model.B @ self.K
            
            # Check if (A-BK) is invertible
            if np.abs(np.linalg.det(A_cl)) < 1e-12:
                logger.warning("Closed-loop A matrix is singular")
                self.N = np.ones((self.model.n_inputs, self.model.n_outputs))
                return self.N
            
            CB_cl = self.model.C @ inv(-A_cl) @ self.model.B
            
            if self.model.n_inputs == self.model.n_outputs:
                self.N = inv(CB_cl)
            else:
                # Pseudo-inverse for non-square systems
                self.N = np.linalg.pinv(CB_cl)
            
            logger.info("Reference tracking matrix computed")
            return self.N
            
        except Exception as e:
            logger.warning(f"Reference tracking design failed: {e}")
            self.N = np.ones((self.model.n_inputs, self.model.n_outputs))
            return self.N
    
    def update(
        self,
        t: float,
        y: np.ndarray,
        r: np.ndarray,
        x: Optional[np.ndarray] = None,
        d: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Update controller and calculate control action.
        
        Args:
            t: Current time
            y: Measured outputs [n_outputs]
            r: Reference signals [n_outputs]
            x: Full state measurement [n_states] (optional, uses observer if not provided)
            d: Known disturbances [n_disturbances] (optional)
            
        Returns:
            Control input u [n_inputs]
        """
        if self.K is None:
            raise RuntimeError("Controller gain K not designed yet")
        
        dt = 0.1  # Default time step
        if self.last_update_time is not None:
            dt = t - self.last_update_time
        
        # State estimation (if full state not available)
        if x is None:
            if self.L is None:
                raise RuntimeError("Observer gain L not designed yet")
            
            # Previous control input (simple approximation)
            u_prev = getattr(self, '_last_u', np.zeros(self.model.n_inputs))
            
            # Observer dynamics: dx_hat/dt = Ax_hat + Bu + L(y - Cx_hat - Du)
            y_pred = self.model.C @ self.x_hat + self.model.D @ u_prev
            error = y - y_pred
            
            # Simple Euler integration
            dxhat_dt = (self.model.A @ self.x_hat + 
                       self.model.B @ u_prev + 
                       self.L @ error)
            
            if self.model.E is not None and d is not None:
                dxhat_dt += self.model.E @ d
            
            self.x_hat += dxhat_dt * dt
            x_current = self.x_hat
        else:
            x_current = x
            self.x_hat = x  # Update estimate with measurement
        
        # Control law: u = -Kx + Nr (state feedback + reference tracking)
        u = -self.K @ x_current
        
        if self.N is not None:
            u += self.N @ r
        
        # Apply control limits if specified
        if hasattr(self, 'control_limits'):
            u = np.clip(u, self.control_limits[0], self.control_limits[1])
        
        self._last_u = u
        self.last_update_time = t
        
        return u
    
    def set_control_limits(self, u_min: np.ndarray, u_max: np.ndarray):
        """Set control input saturation limits."""
        if len(u_min) != self.model.n_inputs or len(u_max) != self.model.n_inputs:
            raise ValueError("Control limits must match number of inputs")
        
        if np.any(u_min >= u_max):
            raise ValueError("u_min must be less than u_max")
        
        self.control_limits = (u_min, u_max)
        logger.info(f"Control limits set: {u_min} to {u_max}")
    
    def reset(self):
        """Reset controller internal state."""
        self.x_hat = np.zeros(self.model.n_states)
        self.integral_states = np.zeros(self.model.n_outputs)
        self.last_update_time = None
        if hasattr(self, '_last_u'):
            delattr(self, '_last_u')
        logger.info(f"StateSpaceController '{self.name}' reset")
    
    def get_controller_info(self) -> Dict[str, Any]:
        """Get controller information and parameters."""
        info = {
            'name': self.name,
            'method': self.control_method,
            'n_states': self.model.n_states,
            'n_inputs': self.model.n_inputs,
            'n_outputs': self.model.n_outputs,
            'controllable': self.model.is_controllable(),
            'observable': self.model.is_observable(),
            'stable': self.model.is_stable()
        }
        
        if self.K is not None:
            A_cl = self.model.A - self.model.B @ self.K
            info['closed_loop_poles'] = eigvals(A_cl)
            info['gain_matrix_K'] = self.K
        
        if self.L is not None:
            A_obs = self.model.A - self.L @ self.model.C
            info['observer_poles'] = eigvals(A_obs)
            info['observer_gain_L'] = self.L
        
        if self.N is not None:
            info['reference_tracking_N'] = self.N
        
        return info
    
    def closed_loop_simulation(
        self,
        t: np.ndarray,
        r: np.ndarray,
        x0: np.ndarray,
        d: Optional[np.ndarray] = None,
        measurement_noise: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate closed-loop system response.
        
        Args:
            t: Time array
            r: Reference signals [len(t) x n_outputs]
            x0: Initial state [n_states]
            d: Disturbances [len(t) x n_disturbances] (optional)
            measurement_noise: Measurement noise [len(t) x n_outputs] (optional)
            
        Returns:
            Tuple of (states, outputs, control_inputs)
        """
        if self.K is None:
            raise RuntimeError("Controller not designed yet")
        
        n_steps = len(t)
        states = np.zeros((n_steps, self.model.n_states))
        outputs = np.zeros((n_steps, self.model.n_outputs))
        controls = np.zeros((n_steps, self.model.n_inputs))
        
        # Initialize
        states[0, :] = x0
        self.reset()
        
        for i in range(n_steps):
            # Current state and output
            x_current = states[i, :]
            y_current = self.model.C @ x_current + self.model.D @ controls[i, :]
            
            # Add measurement noise
            if measurement_noise is not None:
                y_current += measurement_noise[i, :]
            
            outputs[i, :] = y_current
            
            # Controller update
            r_current = r[i, :] if r.ndim > 1 else r
            d_current = d[i, :] if d is not None else None
            
            # Use full state feedback (assume perfect state measurement)
            controls[i, :] = self.update(t[i], y_current, r_current, x_current, d_current)
            
            # Next state (if not last step)
            if i < n_steps - 1:
                dt = t[i+1] - t[i]
                
                # State dynamics
                dxdt = (self.model.A @ x_current + 
                       self.model.B @ controls[i, :])
                
                if d is not None and self.model.E is not None:
                    dxdt += self.model.E @ d_current
                
                states[i+1, :] = x_current + dxdt * dt
        
        return states, outputs, controls

    def describe(self) -> Dict[str, Any]:
        """
        Comprehensive description of the State-Space Controller.
        
        Returns:
            Dictionary containing detailed information about state-space control
            theory, design methods, applications, and current controller status.
        """
        # Analyze current controller matrices
        controller_status = {}
        if self.K is not None:
            # Analyze closed-loop poles
            A_cl = self.model.A - self.model.B @ self.K
            closed_loop_poles = eigvals(A_cl)
            controller_status['closed_loop_poles'] = closed_loop_poles.tolist()
            controller_status['closed_loop_stable'] = np.all(np.real(closed_loop_poles) < 0)
            controller_status['dominant_time_constant'] = -1.0 / np.max(np.real(closed_loop_poles[np.real(closed_loop_poles) < 0]))
        else:
            controller_status['status'] = 'Controller gains not designed yet'
        
        if self.L is not None:
            # Analyze observer poles  
            A_obs = self.model.A - self.L @ self.model.C
            observer_poles = eigvals(A_obs)
            controller_status['observer_poles'] = observer_poles.tolist()
            controller_status['observer_stable'] = np.all(np.real(observer_poles) < 0)
        
        # System analysis
        system_properties = {
            'dimensions': {
                'states': self.model.n_states,
                'inputs': self.model.n_inputs,
                'outputs': self.model.n_outputs,
                'disturbances': getattr(self.model, 'n_disturbances', 0)
            },
            'controllability': self.model.is_controllable(),
            'observability': self.model.is_observable(),
            'stability': self.model.is_stable()
        }
        
        if hasattr(self.model, 'state_names') and self.model.state_names:
            system_properties['state_variables'] = self.model.state_names
        if hasattr(self.model, 'input_names') and self.model.input_names:
            system_properties['input_variables'] = self.model.input_names
        if hasattr(self.model, 'output_names') and self.model.output_names:
            system_properties['output_variables'] = self.model.output_names
        
        return {
            'class_name': 'StateSpaceController',
            'description': 'Advanced multivariable controller using state-space representation',
            'purpose': 'Provides optimal control for MIMO systems with systematic design procedures',
            
            'state_space_theory': {
                'system_representation': {
                    'state_equation': 'dx/dt = Ax + Bu + Ed',
                    'output_equation': 'y = Cx + Du + Fd',
                    'variables': {
                        'x': 'State vector (internal system variables)',
                        'u': 'Input vector (manipulated variables)',
                        'd': 'Disturbance vector',
                        'y': 'Output vector (measured variables)'
                    }
                },
                'matrix_meanings': {
                    'A': 'State matrix - describes internal system dynamics',
                    'B': 'Input matrix - how inputs affect states',
                    'C': 'Output matrix - how states affect outputs',
                    'D': 'Feedthrough matrix - direct input-output coupling',
                    'E': 'Disturbance state matrix - how disturbances affect states',
                    'F': 'Disturbance output matrix - how disturbances affect outputs'
                },
                'advantages': [
                    'Handles MIMO (Multiple Input Multiple Output) systems naturally',
                    'Systematic design procedures (LQR, pole placement)',
                    'Optimal control with explicit performance objectives',
                    'Can handle state constraints and input constraints',
                    'Provides insight into internal system behavior'
                ]
            },
            
            'control_methods': {
                'lqr_control': {
                    'name': 'Linear Quadratic Regulator',
                    'objective': 'Minimize quadratic cost function J = ∫(x\'Qx + u\'Ru) dt',
                    'design_parameters': {
                        'Q': 'State weighting matrix - penalizes state deviations',
                        'R': 'Input weighting matrix - penalizes control effort',
                        'N': 'Cross-weighting matrix (optional)'
                    },
                    'characteristics': [
                        'Guaranteed stability margins (gain margin ≥ 6 dB, phase margin ≥ 60°)',
                        'Optimal in sense of quadratic cost function',
                        'Requires all states to be measured or estimated'
                    ]
                },
                'pole_placement': {
                    'name': 'Pole Placement Control',
                    'objective': 'Place closed-loop poles at desired locations',
                    'design_parameters': {
                        'desired_poles': 'Target locations for closed-loop poles'
                    },
                    'characteristics': [
                        'Direct specification of closed-loop dynamics',
                        'Flexible design for specific performance requirements',
                        'May not guarantee optimality'
                    ]
                },
                'observer_design': {
                    'name': 'State Observer (Kalman Filter)',
                    'objective': 'Estimate unmeasured states from measurements',
                    'design_parameters': {
                        'L': 'Observer gain matrix',
                        'desired_observer_poles': 'Target observer dynamics'
                    },
                    'principle': 'dx̂/dt = Ax̂ + Bu + L(y - Cx̂)'
                }
            },
            
            'system_properties': system_properties,
            
            'design_guidelines': {
                'lqr_tuning': {
                    'Q_matrix_selection': {
                        'diagonal_elements': 'Weight important states more heavily',
                        'relative_magnitudes': 'Balance between different state variables',
                        'units': 'Consider state variable units and typical ranges'
                    },
                    'R_matrix_selection': {
                        'control_effort': 'Larger R values reduce control effort',
                        'actuator_limits': 'Consider actuator constraints',
                        'energy_costs': 'Weight expensive control actions more'
                    },
                    'iteration_process': 'Start with identity matrices, then adjust based on simulation'
                },
                'pole_placement_guidelines': {
                    'dominant_poles': 'Place dominant poles to achieve desired settling time',
                    'non_dominant_poles': 'Place 5-10 times faster than dominant poles',
                    'real_poles': 'Use real poles for no overshoot',
                    'complex_poles': 'Use complex poles for faster response with some overshoot'
                }
            },
            
            'industrial_applications': {
                'distillation_control': {
                    'description': 'Multi-component distillation column control',
                    'states': ['Tray temperatures', 'Component holdups', 'Internal flows'],
                    'inputs': ['Reflux ratio', 'Reboiler duty', 'Feed location'],
                    'outputs': ['Product compositions', 'Product rates'],
                    'benefits': 'Handles strong interactions between control loops'
                },
                'reactor_networks': {
                    'description': 'Multiple reactor systems with recycle streams',
                    'states': ['Concentrations', 'Temperatures', 'Pressures'],
                    'inputs': ['Feed flows', 'Coolant flows', 'Catalyst addition'],
                    'outputs': ['Product quality', 'Conversion', 'Temperature'],
                    'benefits': 'Optimal coordination of multiple units'
                },
                'heat_integration': {
                    'description': 'Heat exchanger networks with energy integration',
                    'states': ['Stream temperatures', 'Heat duties', 'Flow distributions'],
                    'inputs': ['Bypass flows', 'Utility flows', 'Operating pressures'],
                    'outputs': ['Target temperatures', 'Energy consumption'],
                    'benefits': 'Minimizes energy consumption while meeting targets'
                },
                'crystallization_process': {
                    'description': 'Batch crystallization with quality control',
                    'states': ['Concentration', 'Temperature', 'Crystal size distribution'],
                    'inputs': ['Cooling rate', 'Seeding', 'Agitation speed'],
                    'outputs': ['Final crystal size', 'Purity', 'Yield'],
                    'benefits': 'Optimal crystal quality with reproducible batch-to-batch results'
                }
            },
            
            'mathematical_requirements': {
                'controllability': {
                    'definition': 'All states can be controlled by the inputs',
                    'test': 'Rank of controllability matrix [B AB A²B ... Aⁿ⁻¹B] = n',
                    'importance': 'Required for arbitrary pole placement'
                },
                'observability': {
                    'definition': 'All states can be determined from outputs',
                    'test': 'Rank of observability matrix [C; CA; CA²; ...; CAⁿ⁻¹] = n',
                    'importance': 'Required for state estimation'
                },
                'stability': {
                    'definition': 'All eigenvalues of A have negative real parts',
                    'test': 'All eigenvalues in left half-plane',
                    'importance': 'Open-loop stability (system stable without control)'
                }
            },
            
            'implementation_considerations': {
                'computational_requirements': {
                    'matrix_operations': 'Requires linear algebra operations',
                    'real_time_constraints': 'Matrix multiplication at each time step',
                    'memory_usage': 'Stores state estimates and gain matrices'
                },
                'sensor_requirements': {
                    'measurement_noise': 'Kalman filter can handle noisy measurements',
                    'sampling_rate': 'Should be 5-10 times faster than system dynamics',
                    'sensor_placement': 'Affects observability of the system'
                },
                'actuator_considerations': {
                    'saturation_limits': 'Include anti-windup for input constraints',
                    'actuator_dynamics': 'May need to include in state-space model',
                    'failure_modes': 'Design redundancy for critical actuators'
                }
            },
            
            'performance_analysis': {
                'time_domain': {
                    'settling_time': 'Determined by dominant closed-loop poles',
                    'overshoot': 'Related to damping ratio of complex poles',
                    'steady_state_error': 'Usually zero with integral action'
                },
                'frequency_domain': {
                    'bandwidth': 'Frequency range of effective control',
                    'gain_margin': 'Safety margin before instability',
                    'phase_margin': 'Phase safety margin',
                    'sensitivity': 'Disturbance rejection capabilities'
                },
                'robustness': {
                    'model_uncertainty': 'Performance with plant-model mismatch',
                    'parameter_variations': 'Sensitivity to parameter changes',
                    'unmodeled_dynamics': 'High-frequency neglected dynamics'
                }
            },
            
            'current_controller_status': {
                'controller_name': self.name,
                'control_method': self.control_method,
                'model_name': self.model.name,
                'state_estimate': self.x_hat.tolist(),
                'integral_states': self.integral_states.tolist(),
                'last_update_time': self.last_update_time,
                'controller_matrices': {
                    'K_designed': self.K is not None,
                    'L_designed': self.L is not None,
                    'N_designed': self.N is not None
                }
            },
            
            **controller_status,
            
            'advantages_over_pid': {
                'mimo_capability': 'Natural handling of multiple inputs and outputs',
                'optimal_performance': 'Systematic optimization of performance objectives',
                'constraint_handling': 'Can incorporate input and state constraints',
                'disturbance_rejection': 'Predictive disturbance compensation',
                'internal_state_info': 'Provides insight into unmeasured process variables'
            },
            
            'limitations': {
                'model_dependency': 'Requires accurate linear model of the process',
                'computational_cost': 'Higher computational requirements than PID',
                'tuning_complexity': 'More parameters to tune (Q, R matrices)',
                'sensor_requirements': 'May require more measurements or state estimation',
                'linear_assumption': 'Limited to linear or linearized systems'
            },
            
            'recommended_applications': [
                'MIMO systems with strong interactions',
                'Processes where optimal performance is critical',
                'Systems with well-understood dynamics',
                'Applications requiring constraint handling',
                'Processes with expensive control actions'
            ]
        }


def create_reactor_network_model() -> StateSpaceModel:
    """
    Create example state-space model for a reactor network.
    
    Two CSTRs in series with heat integration.
    States: [CA1, T1, CA2, T2] - concentrations and temperatures
    Inputs: [q1, Tc1, Tc2] - feed rate, coolant temperatures
    Outputs: [CA2, T2] - product concentration and temperature
    """
    # State matrix A [4x4]
    A = np.array([
        [-0.5, -0.02,  0.0,  0.0 ],  # dCA1/dt
        [ 0.0, -0.3,   0.0,  0.0 ],  # dT1/dt  
        [ 0.25, 0.0,  -0.4, -0.01],  # dCA2/dt
        [ 0.0,  0.15,  0.0, -0.25]   # dT2/dt
    ])
    
    # Input matrix B [4x3]
    B = np.array([
        [ 0.5,  0.0,  0.0],  # q1 affects CA1
        [ 0.0,  0.2,  0.0],  # Tc1 affects T1
        [ 0.0,  0.0,  0.0],  # 
        [ 0.0,  0.0,  0.15]  # Tc2 affects T2
    ])
    
    # Output matrix C [2x4]
    C = np.array([
        [0, 0, 1, 0],  # CA2 measurement
        [0, 0, 0, 1]   # T2 measurement
    ])
    
    # No direct feedthrough
    D = np.zeros((2, 3))
    
    state_names = ['CA1', 'T1', 'CA2', 'T2']
    input_names = ['q1', 'Tc1', 'Tc2']
    output_names = ['CA2', 'T2']
    
    return StateSpaceModel(
        A, B, C, D,
        state_names=state_names,
        input_names=input_names,
        output_names=output_names,
        name="ReactorNetwork"
    )
