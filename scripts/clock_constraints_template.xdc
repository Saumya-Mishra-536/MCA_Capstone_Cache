# Vivado XDC template only. Do not use until target board/FPGA part and
# actual clock pin/period are confirmed by the course/instructor.
# Example syntax (replace placeholders):
# create_clock -name sys_clk -period <PERIOD_NS> [get_ports clk]
# set_input_delay  <VALUE_NS> -clock sys_clk [get_ports {reset cpu_req cpu_write cpu_addr[*] cpu_wdata[*]}]
# set_output_delay <VALUE_NS> -clock sys_clk [get_ports {cpu_ready cpu_rdata[*]}]
# A meaningful Fmax requires synthesis AND implementation for a selected part,
# valid timing constraints, and timing summary (WNS/TNS).
