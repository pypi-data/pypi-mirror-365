// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
//
//  MIT License
//
//  Copyright (c) 2024-2025 nbiotcloud
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//  SOFTWARE.
//
// =============================================================================
//
// Library:    tests
// Module:     portgroup
// Data Model: PortgroupMod
//             tests/test_svmako.py
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module portgroup #(
  parameter integer width_p = 1
) (
  // main_i: Clock and Reset
  input wire main_clk_i,   // Clock
  input wire main_rst_an_i // Async Reset (Low-Active)
);



  // ------------------------------------------------------
  //  Signals
  // ------------------------------------------------------
  // regf_regf_rx_o_s
  //   regf_regf_rx_o_ctrl_ena_s: bus=RW core=RO in_regf=True
  logic               regf_regf_rx_o_ctrl_ena_rval_s; // Core Read Value
  //   regf_regf_rx_o_rx_data0_s: bus=RO core=RW in_regf=False
  logic [width_p-1:0] regf_regf_rx_o_rx_data0_rbus_s; // Bus Read Value
  //   regf_regf_rx_o_rx_data1_s: bus=RO core=RW in_regf=False
  logic [width_p-1:0] regf_regf_rx_o_rx_data1_rbus_s; // Bus Read Value
  //   regf_regf_rx_o_rx_data2_s: bus=RO core=RW in_regf=False
  logic [width_p-1:0] regf_regf_rx_o_rx_data2_rbus_s; // Bus Read Value
  // regf_regf_tx_o_s
  //   regf_regf_tx_o_ctrl_ena_s: bus=RW core=RO in_regf=True
  logic               regf_regf_tx_o_ctrl_ena_rval_s; // Core Read Value
  //   regf_regf_tx_o_tx_data0_s: bus=RW core=RO in_regf=True
  logic [width_p-1:0] regf_regf_tx_o_tx_data0_rval_s; // Core Read Value


  // ------------------------------------------------------
  //  tests.portgroup_regf: u_regf
  // ------------------------------------------------------
  portgroup_regf #(
    .width_p(1)
  ) u_regf (
    .main_clk_i               (main_clk_i                    ), // Clock
    .main_rst_an_i            (main_rst_an_i                 ), // Async Reset (Low-Active)
    .mem_ena_i                (1'b0                          ), // TODO - Memory Access Enable
    .mem_addr_i               (10'h000                       ), // TODO - Memory Address
    .mem_wena_i               (1'b0                          ), // TODO - Memory Write Enable
    .mem_wdata_i              (32'h00000000                  ), // TODO - Memory Write Data
    .mem_rdata_o              (                              ), // TODO - Memory Read Data
    .mem_err_o                (                              ), // TODO - Memory Access Failed.
    .regf_top_ctrl_ena_rval_o (                              ), // TODO - Core Read Value
    .regf_top_ctrl_busy_rbus_i(1'b0                          ), // TODO - Bus Read Value
    .regf_top_w2_f0_rval_o    (                              ), // TODO - Core Read Value
    .regf_top_w2_f2_rval_o    (                              ), // TODO - Core Read Value
    .regf_rx_ctrl_ena_rval_o  (regf_regf_rx_o_ctrl_ena_rval_s), // Core Read Value
    .regf_rx_rx_data0_rbus_i  (regf_regf_rx_o_rx_data0_rbus_s), // Bus Read Value
    .regf_rx_rx_data1_rbus_i  (regf_regf_rx_o_rx_data1_rbus_s), // Bus Read Value
    .regf_rx_rx_data2_rbus_i  (regf_regf_rx_o_rx_data2_rbus_s), // Bus Read Value
    .regf_tx_ctrl_ena_rval_o  (regf_regf_tx_o_ctrl_ena_rval_s), // Core Read Value
    .regf_tx_tx_data0_rval_o  (regf_regf_tx_o_tx_data0_rval_s), // Core Read Value
    .regf_mod_w2_f0_rval_o    (                              ), // TODO - Core Read Value
    .regf_mod_w2_f2_rval_o    (                              ), // TODO - Core Read Value
    .regf_grpa_w2_f1_rval_o   (                              ), // TODO - Core Read Value
    .regf_grpb_w2_f2_rval_o   (                              )  // TODO - Core Read Value
  );


  // ------------------------------------------------------
  //  tests.portgroup_rx: u_rx
  // ------------------------------------------------------
  portgroup_rx #(
    .width_p(1)
  ) u_rx (
    .main_clk_i          (main_clk_i                    ), // Clock
    .main_rst_an_i       (main_rst_an_i                 ), // Async Reset (Low-Active)
    .regf_ctrl_ena_rval_i(regf_regf_rx_o_ctrl_ena_rval_s), // Core Read Value
    .regf_rx_data0_rbus_o(regf_regf_rx_o_rx_data0_rbus_s), // Bus Read Value
    .regf_rx_data1_rbus_o(regf_regf_rx_o_rx_data1_rbus_s), // Bus Read Value
    .regf_rx_data2_rbus_o(regf_regf_rx_o_rx_data2_rbus_s)  // Bus Read Value
  );


  // ------------------------------------------------------
  //  tests.portgroup_tx: u_tx
  // ------------------------------------------------------
  portgroup_tx #(
    .width_p(1)
  ) u_tx (
    .main_clk_i          (main_clk_i                    ), // Clock
    .main_rst_an_i       (main_rst_an_i                 ), // Async Reset (Low-Active)
    .regf_ctrl_ena_rval_i(regf_regf_tx_o_ctrl_ena_rval_s), // Core Read Value
    .regf_tx_data0_rval_i(regf_regf_tx_o_tx_data0_rval_s)  // Core Read Value
  );

endmodule // portgroup

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
