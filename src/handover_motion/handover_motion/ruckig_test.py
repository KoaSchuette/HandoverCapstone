from ruckig import Ruckig, InputParameter, OutputParameter, Result
import time
otg = Ruckig(1, 0.02)          # calculator: 1 value, 20 ms ticks
inp = InputParameter(1)        # the form
out = OutputParameter(1)       # the answer sheet

inp.current_position = [0.0]
inp.current_velocity = [0.0]
inp.current_acceleration = [0.0]
inp.target_position = [1.0]
inp.target_velocity = [0.0]
inp.target_acceleration = [0.0]
inp.max_velocity = [0.5]
inp.max_acceleration = [1.0]
inp.max_jerk = [2.0]

print(f"{'time (s)':>8} | {'pos':>8} | {'vel':>8} | {'acc':>8}")
print("-" * 41)

result = Result.Working
while result == Result.Working:
    result = otg.update(inp, out)
    print(f"{out.time:8.2f} | "
          f"{out.new_position[0]:8.4f} | "
          f"{out.new_velocity[0]:8.4f} | "
          f"{out.new_acceleration[0]:8.4f}")
    time.sleep(0.1)
    out.pass_to_input(inp)
