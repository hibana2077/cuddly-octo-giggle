**Methodology**

In this study, a windowing approach was employed to evaluate the effects of varying temporal segment lengths (window sizes) on two biomechanical indicators: Motion Smoothness and Movement Stability Index (MSI). The Motion Smoothness metric, based on third-order derivatives of joint angles (jerk), was calculated to assess the temporal continuity and fluidity of movement. Simultaneously, the MSI, defined as the combination of joint trajectory variance and center-of-mass deviations, served as a proxy measure for overall movement stability.

To explore the influence of window size, we implemented an incremental analysis where the last \( N \) frames of a simulated motion dataset were considered for both metrics. A range of window sizes (e.g., 5, 10, 20, 30, 50, 80, 100 frames) was tested. For each window size, Motion Smoothness and MSI values were computed, and their maximum and minimum values across all tested windows were identified. This approach allowed us to observe how increasing or decreasing the temporal scale might amplify or attenuate certain kinematic characteristics in the data.

**Results**

![Experiment 1 Results](./exp1_b.png)

The results demonstrate that the choice of window size significantly impacts the observed values of Motion Smoothness and MSI. As the window size increased, the Motion Smoothness metric exhibited a general downward trend, suggesting that, over longer temporal segments, transient fluctuations in joint kinematics become more averaged, potentially diminishing the prominence of high-frequency variations. Conversely, the MSI values showed an increasing trend with larger window sizes, indicating that longer temporal segments may emphasize cumulative positional drift or accumulated variance in the trajectory, thus presenting an apparently less stable profile.

**Discussion**  

The results demonstrate that the choice of window size significantly impacts the observed values of Motion Smoothness and MSI. As the window size increased, the Motion Smoothness metric exhibited a general downward trend, suggesting that, over longer temporal segments, transient fluctuations in joint kinematics become more averaged, potentially diminishing the prominence of high-frequency variations. Conversely, the MSI values showed an increasing trend with larger window sizes, indicating that longer temporal segments may emphasize cumulative positional drift or accumulated variance in the trajectory, thus presenting an apparently less stable profile.

These contrasting responses highlight the complexity inherent in biomechanical data: short windows may be more sensitive to rapid changes or short-term perturbations in motion, while longer windows may capture broader, more global fluctuations. The interplay between local and global properties of the movement likely influences these metrics, emphasizing the need to carefully select or justify the window size depending on the research objectives and the nature of the motion under study.

**Conclusion**  

In summary, the findings underscore the importance of considering window size when analyzing time-dependent biomechanical indices. Varying the temporal scale can yield divergent interpretations of movement fluidity and stability. Researchers should therefore adopt a windowing strategy that aligns with their investigative goals, whether to capture fine-grained temporal transitions or to assess global movement trends. By doing so, more robust and contextually meaningful insights into human movement behavior and motor control can be achieved.