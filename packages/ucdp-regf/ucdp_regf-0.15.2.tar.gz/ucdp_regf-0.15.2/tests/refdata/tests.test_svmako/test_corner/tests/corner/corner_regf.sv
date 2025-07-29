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
// Module:     corner_regf
// Data Model: RegfMod
//             tests/test_svmako.py
//
//
// Addressing-Width: data
// Size:             1024x32 (4 KB)
//
//
// Offset       Word     Field      Bus/Core    Reset    Const    Impl
// dec / hex
// -----------  -------  ---------  ----------  -------  -------  ------
// 0 / 0        ctrl
//              [0]      .ena       RW/RO       0        False    regf
//              [4]      .busy      RO/RW       0        False    core
//              [5]      .start     RW/RO       0        False    regf
//              [6]      .status    RO/RW       0        False    core
//              [10:7]   .ver       RO/RO       0xC      True     regf
//              [11]     .spec1     RC/RW       0        False    core
// 5:1 / 5:1    txdata
//              [7:0]    .bytes     RW/RO       0x0      False    regf
// 8:6 / 8:6    dims
//              [0]      .roval     RO/RW       0        False    core
//              [1]      .wrval     RW/RO       0        False    regf
//              [2]      .spec2     RW/RC       0        False    core
//              [3]      .spec3     RC/RW       0        False    regf
// 9 / 9        guards
//              [0]      .once      WL/RO       0        False    regf
//              [1]      .coreonce  WL/RO       0        False    core
//              [2]      .busonce   WL/RO       0        False    core
//              [3]      .single    WL/RO       0        False    regf
//              [4]      .onetime   WL/RO       0        False    regf
//              [8:5]    .guard_a   RWL/RO      0x0      False    regf
//              [12:9]   .guard_b   RW/RO       0x0      False    regf
//              [16:13]  .guard_c   RW/RO       0x0      False    regf
//              [17]     .cprio     RW/RW       0        False    regf
//              [18]     .bprio     RW/RW       0        False    regf
//              [19]     .grdport   RW/RO       0        False    regf
// 11:10 / B:A  grddim
//              [11:0]   .num       RW/RO       0x0      False    core
//              [14:12]  .const     RO/RO       0x5      True     regf
//              [26:15]  .int       RW/RO       0x0      False    core
// 12 / C       mixint
//              [3:0]    .r_int     RW/RO       0x0      False    regf
//              [7:4]    .r_uint    RW/RO       0x0      False    regf
//              [11:8]   .c_int     RW/RO       -0x3     False    core
// 13 / D       wide0
//              [15:0]   .a         RW/RO       0x0      False    regf
//              [31:16]  .b         RW/RO       0x0      False    regf
// 14 / E       wide1
//              [15:0]   .c         RW/RO       0x0      False    regf
//              [31:16]  .d         RW/RO       0x0      False    regf
// 15 / F       wonly
//              [0]      .wo        WO/RO       0        False    regf
// 16 / 10      full
//              [31:0]   .f0        WCR/RO      0x0      False    regf
//
//
// Mnemonic    ReadOp      WriteOp
// ----------  ----------  ------------
// RC          Read-Clear
// RO          Read
// RW          Read        Write
// RWL         Read        Write Locked
// WCR         Read        WC
// WL                      Write Locked
// WO                      Write
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module corner_regf (
  // main_i: Clock and Reset
  input  wire                main_clk_i,                          // Clock
  input  wire                main_rst_an_i,                       // Async Reset (Low-Active)
  // mem_i
  input  wire                mem_ena_i,                           // Memory Access Enable
  input  wire         [9:0]  mem_addr_i,                          // Memory Address
  input  wire                mem_wena_i,                          // Memory Write Enable
  input  wire         [31:0] mem_wdata_i,                         // Memory Write Data
  output logic        [31:0] mem_rdata_o,                         // Memory Read Data
  output logic               mem_err_o,                           // Memory Access Failed.
  // -
  input  wire                grd_i,                               // Enable
  // regf_o
  //   regf_ctrl_ena_o: bus=RW core=RO in_regf=True
  output logic               regf_ctrl_ena_rval_o,                // Core Read Value
  //   regf_ctrl_busy_o: bus=RO core=RW in_regf=False
  input  wire                regf_ctrl_busy_rbus_i,               // Bus Read Value
  //   regf_grpa_o
  //     regf_grpa_ctrl_start_o: bus=RW core=RO in_regf=True
  output logic               regf_grpa_ctrl_start_rval_o,         // Core Read Value
  //     regf_grpa_ctrl_status_o: bus=RO core=RW in_regf=False
  input  wire                regf_grpa_ctrl_status_rbus_i,        // Bus Read Value
  //     regf_grpa_grddim_int_o: bus=RW core=RO in_regf=False
  output logic               regf_grpa_grddim_int_wr_o     [0:1], // Bus Write Strobe
  output logic        [11:0] regf_grpa_grddim_int_wbus_o   [0:1], // Bus Write Value
  input  wire         [11:0] regf_grpa_grddim_int_rbus_i   [0:1], // Bus Read Value
  //   regf_grpb_o
  //     regf_grpb_ctrl_start_o: bus=RW core=RO in_regf=True
  output logic               regf_grpb_ctrl_start_rval_o,         // Core Read Value
  //   regf_ctrl_ver_o: bus=RO core=RO in_regf=True
  output logic        [3:0]  regf_ctrl_ver_rval_o,                // Core Read Value
  //   regf_grpc_o
  //     regf_grpc_ctrl_spec1_o: bus=RC core=RW in_regf=False
  input  wire                regf_grpc_ctrl_spec1_rbus_i,         // Bus Read Value
  output logic               regf_grpc_ctrl_spec1_rd_o,           // Bus Read Strobe
  //     regf_grpc_dims_spec2_o: bus=RW core=RC in_regf=False
  output logic               regf_grpc_dims_spec2_wr_o     [0:2], // Bus Write Strobe
  output logic               regf_grpc_dims_spec2_wbus_o   [0:2], // Bus Write Value
  input  wire                regf_grpc_dims_spec2_rbus_i   [0:2], // Bus Read Value
  //     regf_grpc_dims_spec3_o: bus=RC core=RW in_regf=True
  input  wire                regf_grpc_dims_spec3_wr_i     [0:2], // Core Write Strobe
  input  wire                regf_grpc_dims_spec3_wval_i   [0:2], // Core Write Value
  output logic               regf_grpc_dims_spec3_rval_o   [0:2], // Core Read Value
  //   regf_txdata_bytes_o: bus=RW core=RO in_regf=True
  output logic        [7:0]  regf_txdata_bytes_rval_o      [0:4], // Core Read Value
  //   regf_dims_roval_o: bus=RO core=RW in_regf=False
  input  wire                regf_dims_roval_rbus_i        [0:2], // Bus Read Value
  //   regf_dims_wrval_o: bus=RW core=RO in_regf=True
  output logic               regf_dims_wrval_upd_o         [0:2], // Update Strobe
  output logic               regf_dims_wrval_rval_o        [0:2], // Core Read Value
  //   regf_guards_once_o: bus=WL core=RO in_regf=True
  output logic               regf_guards_once_rval_o       [0:0], // Core Read Value
  //   regf_guards_coreonce_o: bus=WL core=RO in_regf=False
  output logic               regf_guards_coreonce_wr_o     [0:0], // Bus Write Strobe
  output logic               regf_guards_coreonce_wbus_o   [0:0], // Bus Write Value
  //   regf_guards_busonce_o: bus=WL core=RO in_regf=False
  output logic               regf_guards_busonce_wr_o      [0:0], // Bus Write Strobe
  output logic               regf_guards_busonce_wbus_o    [0:0], // Bus Write Value
  //   regf_guards_single_o: bus=WL core=RO in_regf=True
  output logic               regf_guards_single_rval_o     [0:0], // Core Read Value
  //   regf_guards_onetime_o: bus=WL core=RO in_regf=True
  output logic               regf_guards_onetime_rval_o    [0:0], // Core Read Value
  //   regf_guards_guard_a_o: bus=RWL core=RO in_regf=True
  output logic        [3:0]  regf_guards_guard_a_rval_o    [0:0], // Core Read Value
  //   regf_guards_guard_b_o: bus=RW core=RO in_regf=True
  output logic        [3:0]  regf_guards_guard_b_rval_o    [0:0], // Core Read Value
  //   regf_guards_guard_c_o: bus=RW core=RO in_regf=True
  output logic               regf_guards_guard_c_upd_o     [0:0], // Update Strobe
  output logic        [3:0]  regf_guards_guard_c_rval_o    [0:0], // Core Read Value
  //   regf_guards_cprio_o: bus=RW core=RW in_regf=True
  input  wire                regf_guards_cprio_wr_i        [0:0], // Core Write Strobe
  input  wire                regf_guards_cprio_wval_i      [0:0], // Core Write Value
  output logic               regf_guards_cprio_rval_o      [0:0], // Core Read Value
  //   regf_guards_bprio_o: bus=RW core=RW in_regf=True
  input  wire                regf_guards_bprio_wr_i        [0:0], // Core Write Strobe
  input  wire                regf_guards_bprio_wval_i      [0:0], // Core Write Value
  output logic               regf_guards_bprio_rval_o      [0:0], // Core Read Value
  //   regf_guards_grdport_o: bus=RW core=RO in_regf=True
  output logic               regf_guards_grdport_rval_o    [0:0], // Core Read Value
  //   regf_grddim_num_o: bus=RW core=RO in_regf=False
  output logic               regf_grddim_num_wr_o          [0:1], // Bus Write Strobe
  output logic        [11:0] regf_grddim_num_wbus_o        [0:1], // Bus Write Value
  input  wire         [11:0] regf_grddim_num_rbus_i        [0:1], // Bus Read Value
  //   regf_grddim_const_o: bus=RO core=RO in_regf=True
  output logic        [2:0]  regf_grddim_const_rval_o      [0:1], // Core Read Value
  //   regf_mixint_r_int_o: bus=RW core=RO in_regf=True
  output logic signed [3:0]  regf_mixint_r_int_rval_o,            // Core Read Value
  //   regf_mixint_r_uint_o: bus=RW core=RO in_regf=True
  output logic        [3:0]  regf_mixint_r_uint_rval_o,           // Core Read Value
  //   regf_mixint_c_int_o: bus=RW core=RO in_regf=False
  input  wire signed  [3:0]  regf_mixint_c_int_rbus_i,            // Bus Read Value
  output logic signed [3:0]  regf_mixint_c_int_wbus_o,            // Bus Write Value
  output logic               regf_mixint_c_int_wr_o,              // Bus Write Strobe
  //   regf_wide_a_o: bus=RW core=RO in_regf=True
  output logic        [15:0] regf_wide_a_rval_o,                  // Core Read Value
  //   regf_wide_b_o: bus=RW core=RO in_regf=True
  output logic        [15:0] regf_wide_b_rval_o,                  // Core Read Value
  //   regf_base_o: bus=RW core=RO in_regf=True
  output logic        [15:0] regf_base_rval_o,                    // Core Read Value
  //   regf_wide_d_o: bus=RW core=RO in_regf=True
  output logic        [15:0] regf_wide_d_rval_o,                  // Core Read Value
  //   regf_wonly_wo_o: bus=WO core=RO in_regf=True
  output logic               regf_wonly_wo_rval_o,                // Core Read Value
  //   regf_full_f0_o: bus=WCR core=RO in_regf=True
  output logic        [31:0] regf_full_f0_rval_o,                 // Core Read Value
  output logic               regf_full_f0_upd_o,                  // Update Strobe
  // regfword_o
  // -
  input  wire                another_grd_i
);




  // ------------------------------------------------------
  //  Local Parameter
  // ------------------------------------------------------
  localparam logic [3:0] data_ctrl_ver_c           = 4'hC;       // ctrl / ver
  localparam logic [2:0] data_grddim_const_c [0:1] = '{2{3'h5}}; // grddim / const


  // ------------------------------------------------------
  //  Signals
  // ------------------------------------------------------
  logic               data_ctrl_ena_r;                        // Word ctrl
  logic               data_ctrl_start_r;
  logic        [7:0]  data_txdata_bytes_r              [0:4]; // Word txdata
  logic               data_dims_wrval_r                [0:2]; // Word dims
  logic               data_dims_spec3_r                [0:2];
  logic               upd_strb_dims_wrval_r            [0:2];
  logic               data_guards_once_r               [0:0]; // Word guards
  logic               data_guards_single_r             [0:0];
  logic               data_guards_onetime_r            [0:0];
  logic        [3:0]  data_guards_guard_a_r            [0:0];
  logic        [3:0]  data_guards_guard_b_r            [0:0];
  logic        [3:0]  data_guards_guard_c_r            [0:0];
  logic               data_guards_cprio_r              [0:0];
  logic               data_guards_bprio_r              [0:0];
  logic               data_guards_grdport_r            [0:0];
  logic               bus_wronce_guards_flg0_r         [0:0];
  logic               bus_wronce_guards_flg1_r         [0:0];
  logic               bus_wronce_guards_flg2_r         [0:0];
  logic               upd_strb_guards_guard_c_r        [0:0];
  logic               upd_strb_grddim_num_r            [0:1];
  logic signed [3:0]  data_mixint_r_int_r;                    // Word mixint
  logic        [3:0]  data_mixint_r_uint_r;
  logic        [15:0] data_wide_a_r;                          // Word wide0
  logic        [15:0] data_wide_b_r;
  logic        [15:0] data_base_r;                            // Word wide1
  logic        [15:0] data_wide_d_r;
  logic               data_wonly_wo_r;                        // Word wonly
  logic        [31:0] data_full_f0_r;                         // Word full
  logic               upd_strb_full_f0_r;
  logic               bus_ctrl_wren_s;                        // bus word write enables
  logic               bus_txdata_wren_s                [0:4];
  logic               bus_dims_wren_s                  [0:2];
  logic               bus_guards_wren_s                [0:0];
  logic               bus_grddim_wren_s                [0:1];
  logic               bus_mixint_wren_s;
  logic               bus_wide0_wren_s;
  logic               bus_wide1_wren_s;
  logic               bus_wonly_wren_s;
  logic               bus_full_wren_s;
  logic               bus_ctrl_rden_s;                        // bus word read-modify enables
  logic               bus_dims_rden_s                  [0:2];
  logic               bus_guards_wrguard_0_flg0_wren_s [0:0]; // special update condition signals
  logic               bus_guards_wrguard_1_flg1_wren_s [0:0];
  logic               bus_guards_flg2_wren_s           [0:0];
  logic               bus_guards_wrguard_1_wren_s      [0:0];
  logic               bus_guards_wrguard_2_wren_s      [0:0];
  logic               bus_grddim_wrguard_1_wren_s      [0:1];
  logic               bus_grddim_wrguard_3_wren_s      [0:1];
  logic               bus_wonly_wrguard_4_wren_s;
  logic               bus_full_wrguard_4_wren_s;
  logic               bus_wrguard_0_s;                        // write guards
  logic               bus_wrguard_1_s;
  logic               bus_wrguard_2_s;
  logic               bus_wrguard_3_s;
  logic               bus_wrguard_4_s;
  logic               bus_guards_grderr_s              [0:0]; // guard errors
  logic               bus_wonly_grderr_s;
  logic               dims_spec2_wbus_s                [0:2]; // intermediate signals for bus-writes to in-core fields
  logic               guards_coreonce_wbus_s           [0:0];
  logic               guards_busonce_wbus_s            [0:0];
  logic        [11:0] grddim_num_wbus_s                [0:1];
  logic        [11:0] grddim_int_wbus_s                [0:1];
  logic signed [3:0]  mixint_c_int_wbus_s;

  // ------------------------------------------------------
  // address decoding
  // ------------------------------------------------------
  always_comb begin: proc_bus_addr_dec
    // defaults
    mem_err_o = 1'b0;
    bus_ctrl_wren_s   = 1'b0;
    bus_ctrl_rden_s   = 1'b0;
    bus_txdata_wren_s = '{5{1'b0}};
    bus_dims_wren_s   = '{3{1'b0}};
    bus_dims_rden_s   = '{3{1'b0}};
    bus_guards_wren_s = '{1{1'b0}};
    bus_grddim_wren_s = '{2{1'b0}};
    bus_mixint_wren_s = 1'b0;
    bus_wide0_wren_s  = 1'b0;
    bus_wide1_wren_s  = 1'b0;
    bus_wonly_wren_s  = 1'b0;
    bus_full_wren_s   = 1'b0;

    // decode address
    if (mem_ena_i == 1'b1) begin
      case (mem_addr_i)
        10'h000: begin
          bus_ctrl_wren_s = mem_wena_i;
          bus_ctrl_rden_s = ~mem_wena_i;
        end
        10'h001: begin
          bus_txdata_wren_s[0] = mem_wena_i;
        end
        10'h002: begin
          bus_txdata_wren_s[1] = mem_wena_i;
        end
        10'h003: begin
          bus_txdata_wren_s[2] = mem_wena_i;
        end
        10'h004: begin
          bus_txdata_wren_s[3] = mem_wena_i;
        end
        10'h005: begin
          bus_txdata_wren_s[4] = mem_wena_i;
        end
        10'h006: begin
          bus_dims_wren_s[0] = mem_wena_i;
          bus_dims_rden_s[0] = ~mem_wena_i;
        end
        10'h007: begin
          bus_dims_wren_s[1] = mem_wena_i;
          bus_dims_rden_s[1] = ~mem_wena_i;
        end
        10'h008: begin
          bus_dims_wren_s[2] = mem_wena_i;
          bus_dims_rden_s[2] = ~mem_wena_i;
        end
        10'h009: begin
          mem_err_o = bus_guards_grderr_s[0];
          bus_guards_wren_s[0] = mem_wena_i;
        end
        10'h00A: begin
          bus_grddim_wren_s[0] = mem_wena_i;
        end
        10'h00B: begin
          bus_grddim_wren_s[1] = mem_wena_i;
        end
        10'h00C: begin
          bus_mixint_wren_s = mem_wena_i;
        end
        10'h00D: begin
          bus_wide0_wren_s = mem_wena_i;
        end
        10'h00E: begin
          bus_wide1_wren_s = mem_wena_i;
        end
        10'h00F: begin
          mem_err_o = ~mem_wena_i | bus_wonly_grderr_s;
          bus_wonly_wren_s = mem_wena_i;
        end
        10'h010: begin
          bus_full_wren_s = mem_wena_i;
        end
        default: begin
          mem_err_o = 1'b1;
        end
      endcase
    end
  end

  // ------------------------------------------------------
  // write guard expressions
  // ------------------------------------------------------
  assign bus_wrguard_0_s = data_ctrl_ena_r & regf_ctrl_busy_rbus_i;
  assign bus_wrguard_1_s = regf_ctrl_busy_rbus_i;
  assign bus_wrguard_2_s = ~(grd_i & regf_ctrl_busy_rbus_i & another_grd_i);
  assign bus_wrguard_3_s = regf_grpc_ctrl_spec1_rbus_i;
  assign bus_wrguard_4_s = grd_i;

  // ------------------------------------------------------
  // write guard errors
  // ------------------------------------------------------
  assign bus_guards_grderr_s[0] = mem_wena_i &  ( ((~bus_wrguard_0_s | ~bus_wronce_guards_flg0_r[0]) & (|(data_guards_once_r[0] ^ mem_wdata_i[0]))) |
                                                  (~bus_wrguard_1_s | ~bus_wronce_guards_flg1_r[0]) |
                                                  (~bus_wronce_guards_flg2_r[0] & (|(data_guards_single_r[0] ^ mem_wdata_i[3]))) |
                                                  (~bus_wronce_guards_flg2_r[0] & (|(data_guards_onetime_r[0] ^ mem_wdata_i[4]))) |
                                                  ((~bus_wrguard_0_s | ~bus_wronce_guards_flg0_r[0]) & (|(data_guards_guard_a_r[0] ^ mem_wdata_i[8:5]))) |
                                                  (~bus_wrguard_1_s & (|(data_guards_guard_b_r[0] ^ mem_wdata_i[12:9]))) |
                                                  (~bus_wrguard_1_s & (|(data_guards_guard_c_r[0] ^ mem_wdata_i[16:13]))) |
                                                  (~bus_wrguard_2_s & (|(data_guards_grdport_r[0] ^ mem_wdata_i[19]))) );
  assign bus_wonly_grderr_s     = mem_wena_i &  ~bus_wrguard_4_s;

  // ------------------------------------------------------
  // special update conditions
  // ------------------------------------------------------
  assign bus_guards_wrguard_0_flg0_wren_s[0]  = bus_guards_wren_s[0] & bus_wrguard_0_s & bus_wronce_guards_flg0_r[0];
  assign bus_guards_wrguard_1_flg1_wren_s[0]  = bus_guards_wren_s[0] & bus_wrguard_1_s & bus_wronce_guards_flg1_r[0];
  assign bus_guards_flg2_wren_s[0]            = bus_guards_wren_s[0] & bus_wronce_guards_flg2_r[0];
  assign bus_guards_wrguard_1_wren_s[0]       = bus_guards_wren_s[0] & bus_wrguard_1_s;
  assign bus_guards_wrguard_2_wren_s[0]       = bus_guards_wren_s[0] & bus_wrguard_2_s;
  assign bus_grddim_wrguard_1_wren_s[0]       = bus_grddim_wren_s[0] & bus_wrguard_1_s;
  assign bus_grddim_wrguard_1_wren_s[1]       = bus_grddim_wren_s[1] & bus_wrguard_1_s;
  assign bus_grddim_wrguard_3_wren_s[0]       = bus_grddim_wren_s[0] & bus_wrguard_3_s;
  assign bus_grddim_wrguard_3_wren_s[1]       = bus_grddim_wren_s[1] & bus_wrguard_3_s;
  assign bus_wonly_wrguard_4_wren_s           = bus_wonly_wren_s & bus_wrguard_4_s;
  assign bus_full_wrguard_4_wren_s            = bus_full_wren_s & bus_wrguard_4_s;

  // ------------------------------------------------------
  // in-regf storage
  // ------------------------------------------------------
  always_ff @ (posedge main_clk_i or negedge main_rst_an_i) begin: proc_regf_flops
    if (main_rst_an_i == 1'b0) begin
      // Word: ctrl
      data_ctrl_ena_r           <= 1'b0;
      data_ctrl_start_r         <= 1'b0;
      // Word: txdata
      data_txdata_bytes_r       <= '{5{8'h00}};
      // Word: dims
      data_dims_wrval_r         <= '{3{1'b0}};
      data_dims_spec3_r         <= '{3{1'b0}};
      upd_strb_dims_wrval_r     <= '{3{1'b0}};
      // Word: guards
      data_guards_once_r        <= '{1{1'b0}};
      data_guards_single_r      <= '{1{1'b0}};
      data_guards_onetime_r     <= '{1{1'b0}};
      data_guards_guard_a_r     <= '{1{4'h0}};
      data_guards_guard_b_r     <= '{1{4'h0}};
      data_guards_guard_c_r     <= '{1{4'h0}};
      data_guards_cprio_r       <= '{1{1'b0}};
      data_guards_bprio_r       <= '{1{1'b0}};
      data_guards_grdport_r     <= '{1{1'b0}};
      bus_wronce_guards_flg0_r  <= '{1{1'b1}};
      bus_wronce_guards_flg1_r  <= '{1{1'b1}};
      bus_wronce_guards_flg2_r  <= '{1{1'b1}};
      upd_strb_guards_guard_c_r <= '{1{1'b0}};
      // Word: grddim
      upd_strb_grddim_num_r     <= '{2{1'b0}};
      // Word: mixint
      data_mixint_r_int_r       <= 4'sh0;
      data_mixint_r_uint_r      <= 4'h0;
      // Word: wide0
      data_wide_a_r             <= 16'h0000;
      data_wide_b_r             <= 16'h0000;
      // Word: wide1
      data_base_r               <= 16'h0000;
      data_wide_d_r             <= 16'h0000;
      // Word: wonly
      data_wonly_wo_r           <= 1'b0;
      // Word: full
      data_full_f0_r            <= 32'h00000000;
      upd_strb_full_f0_r        <= 1'b0;
    end else begin
      if (bus_ctrl_wren_s == 1'b1) begin
        data_ctrl_ena_r <= mem_wdata_i[0];
      end
      if (bus_ctrl_wren_s == 1'b1) begin
        data_ctrl_start_r <= mem_wdata_i[5];
      end
      if (bus_txdata_wren_s[0] == 1'b1) begin
        data_txdata_bytes_r[0] <= mem_wdata_i[7:0];
      end
      if (bus_txdata_wren_s[1] == 1'b1) begin
        data_txdata_bytes_r[1] <= mem_wdata_i[7:0];
      end
      if (bus_txdata_wren_s[2] == 1'b1) begin
        data_txdata_bytes_r[2] <= mem_wdata_i[7:0];
      end
      if (bus_txdata_wren_s[3] == 1'b1) begin
        data_txdata_bytes_r[3] <= mem_wdata_i[7:0];
      end
      if (bus_txdata_wren_s[4] == 1'b1) begin
        data_txdata_bytes_r[4] <= mem_wdata_i[7:0];
      end
      if (bus_dims_wren_s[0] == 1'b1) begin
        data_dims_wrval_r[0] <= mem_wdata_i[1];
      end
      upd_strb_dims_wrval_r[0] <= bus_dims_wren_s[0];
      if (bus_dims_wren_s[1] == 1'b1) begin
        data_dims_wrval_r[1] <= mem_wdata_i[1];
      end
      upd_strb_dims_wrval_r[1] <= bus_dims_wren_s[1];
      if (bus_dims_wren_s[2] == 1'b1) begin
        data_dims_wrval_r[2] <= mem_wdata_i[1];
      end
      upd_strb_dims_wrval_r[2] <= bus_dims_wren_s[2];
      if (regf_grpc_dims_spec3_wr_i[0] == 1'b1) begin
        data_dims_spec3_r[0] <= regf_grpc_dims_spec3_wval_i[0];
      end else if (bus_dims_rden_s[0] == 1'b1) begin
        data_dims_spec3_r[0] <= 1'b0;
      end
      if (regf_grpc_dims_spec3_wr_i[1] == 1'b1) begin
        data_dims_spec3_r[1] <= regf_grpc_dims_spec3_wval_i[1];
      end else if (bus_dims_rden_s[1] == 1'b1) begin
        data_dims_spec3_r[1] <= 1'b0;
      end
      if (regf_grpc_dims_spec3_wr_i[2] == 1'b1) begin
        data_dims_spec3_r[2] <= regf_grpc_dims_spec3_wval_i[2];
      end else if (bus_dims_rden_s[2] == 1'b1) begin
        data_dims_spec3_r[2] <= 1'b0;
      end
      if (bus_guards_wrguard_0_flg0_wren_s[0] == 1'b1) begin
        data_guards_once_r[0] <= mem_wdata_i[0];
      end
      if (bus_guards_flg2_wren_s[0] == 1'b1) begin
        data_guards_single_r[0] <= mem_wdata_i[3];
      end
      if (bus_guards_flg2_wren_s[0] == 1'b1) begin
        data_guards_onetime_r[0] <= mem_wdata_i[4];
      end
      if (bus_guards_wrguard_0_flg0_wren_s[0] == 1'b1) begin
        data_guards_guard_a_r[0] <= mem_wdata_i[8:5];
      end
      if (bus_guards_wrguard_1_wren_s[0] == 1'b1) begin
        data_guards_guard_b_r[0] <= mem_wdata_i[12:9];
      end
      if (bus_guards_wrguard_1_wren_s[0] == 1'b1) begin
        data_guards_guard_c_r[0] <= mem_wdata_i[16:13];
      end
      upd_strb_guards_guard_c_r[0] <= bus_guards_wrguard_1_wren_s[0];
      if (regf_guards_cprio_wr_i[0] == 1'b1) begin
        data_guards_cprio_r[0] <= regf_guards_cprio_wval_i[0];
      end else if (bus_guards_wren_s[0] == 1'b1) begin
        data_guards_cprio_r[0] <= mem_wdata_i[17];
      end
      if (bus_guards_wren_s[0] == 1'b1) begin
        data_guards_bprio_r[0] <= mem_wdata_i[18];
      end else if (regf_guards_bprio_wr_i[0] == 1'b1) begin
        data_guards_bprio_r[0] <= regf_guards_bprio_wval_i[0];
      end
      if (bus_guards_wrguard_2_wren_s[0] == 1'b1) begin
        data_guards_grdport_r[0] <= mem_wdata_i[19];
      end
      if (bus_mixint_wren_s == 1'b1) begin
        data_mixint_r_int_r <= signed'(mem_wdata_i[3:0]);
      end
      if (bus_mixint_wren_s == 1'b1) begin
        data_mixint_r_uint_r <= mem_wdata_i[7:4];
      end
      if (bus_wide0_wren_s == 1'b1) begin
        data_wide_a_r <= mem_wdata_i[15:0];
      end
      if (bus_wide0_wren_s == 1'b1) begin
        data_wide_b_r <= mem_wdata_i[31:16];
      end
      if (bus_wide1_wren_s == 1'b1) begin
        data_base_r <= mem_wdata_i[15:0];
      end
      if (bus_wide1_wren_s == 1'b1) begin
        data_wide_d_r <= mem_wdata_i[31:16];
      end
      if (bus_wonly_wrguard_4_wren_s == 1'b1) begin
        data_wonly_wo_r <= mem_wdata_i[0];
      end
      if (bus_full_wrguard_4_wren_s == 1'b1) begin
        data_full_f0_r <= 32'h00000000;
      end
      upd_strb_full_f0_r <= bus_full_wrguard_4_wren_s;
      if ((bus_guards_wren_s[0] == 1'b1) && (bus_wrguard_0_s == 1'b1)) begin
        bus_wronce_guards_flg0_r[0] <= 1'b0;
      end
      if ((bus_guards_wren_s[0] == 1'b1) && (bus_wrguard_1_s == 1'b1)) begin
        bus_wronce_guards_flg1_r[0] <= 1'b0;
      end
      if (bus_guards_wren_s[0] == 1'b1) begin
        bus_wronce_guards_flg2_r[0] <= 1'b0;
      end
    end
  end

  // ------------------------------------------------------
  // intermediate signals for in-core bus-writes
  // ------------------------------------------------------
  assign dims_spec2_wbus_s[0]      = bus_dims_wren_s[0] ? mem_wdata_i[2] : 1'b0;
  assign dims_spec2_wbus_s[1]      = bus_dims_wren_s[1] ? mem_wdata_i[2] : 1'b0;
  assign dims_spec2_wbus_s[2]      = bus_dims_wren_s[2] ? mem_wdata_i[2] : 1'b0;
  assign guards_coreonce_wbus_s[0] = bus_guards_wrguard_1_flg1_wren_s[0] ? mem_wdata_i[1] : 1'b0;
  assign guards_busonce_wbus_s[0]  = bus_guards_wrguard_1_flg1_wren_s[0] ? mem_wdata_i[2] : 1'b0;
  assign grddim_num_wbus_s[0]      = bus_grddim_wrguard_1_wren_s[0] ? mem_wdata_i[11:0] : 12'h000;
  assign grddim_num_wbus_s[1]      = bus_grddim_wrguard_1_wren_s[1] ? mem_wdata_i[11:0] : 12'h000;
  assign grddim_int_wbus_s[0]      = bus_grddim_wrguard_3_wren_s[0] ? mem_wdata_i[26:15] : 12'h000;
  assign grddim_int_wbus_s[1]      = bus_grddim_wrguard_3_wren_s[1] ? mem_wdata_i[26:15] : 12'h000;
  assign mixint_c_int_wbus_s       = bus_mixint_wren_s ? signed'(mem_wdata_i[11:8]) : 4'sh0;

  // ------------------------------------------------------
  //  Bus Read-Mux
  // ------------------------------------------------------
  always_comb begin: proc_bus_rd
    if ((mem_ena_i == 1'b1) && (mem_wena_i == 1'b0)) begin
      case (mem_addr_i)
        10'h000: begin
          mem_rdata_o = {20'h00000, regf_grpc_ctrl_spec1_rbus_i, data_ctrl_ver_c, regf_grpa_ctrl_status_rbus_i, data_ctrl_start_r, regf_ctrl_busy_rbus_i, 3'h0, data_ctrl_ena_r};
        end
        10'h001: begin
          mem_rdata_o = {24'h000000, data_txdata_bytes_r[0]};
        end
        10'h002: begin
          mem_rdata_o = {24'h000000, data_txdata_bytes_r[1]};
        end
        10'h003: begin
          mem_rdata_o = {24'h000000, data_txdata_bytes_r[2]};
        end
        10'h004: begin
          mem_rdata_o = {24'h000000, data_txdata_bytes_r[3]};
        end
        10'h005: begin
          mem_rdata_o = {24'h000000, data_txdata_bytes_r[4]};
        end
        10'h006: begin
          mem_rdata_o = {28'h0000000, data_dims_spec3_r[0], regf_grpc_dims_spec2_rbus_i[0], data_dims_wrval_r[0], regf_dims_roval_rbus_i[0]};
        end
        10'h007: begin
          mem_rdata_o = {28'h0000000, data_dims_spec3_r[1], regf_grpc_dims_spec2_rbus_i[1], data_dims_wrval_r[1], regf_dims_roval_rbus_i[1]};
        end
        10'h008: begin
          mem_rdata_o = {28'h0000000, data_dims_spec3_r[2], regf_grpc_dims_spec2_rbus_i[2], data_dims_wrval_r[2], regf_dims_roval_rbus_i[2]};
        end
        10'h009: begin
          mem_rdata_o = {12'h000, data_guards_grdport_r[0], data_guards_bprio_r[0], data_guards_cprio_r[0], data_guards_guard_c_r[0], data_guards_guard_b_r[0], data_guards_guard_a_r[0], 5'h00};
        end
        10'h00A: begin
          mem_rdata_o = {5'h00, regf_grpa_grddim_int_rbus_i[0], data_grddim_const_c[0], regf_grddim_num_rbus_i[0]};
        end
        10'h00B: begin
          mem_rdata_o = {5'h00, regf_grpa_grddim_int_rbus_i[1], data_grddim_const_c[1], regf_grddim_num_rbus_i[1]};
        end
        10'h00C: begin
          mem_rdata_o = {20'h00000, unsigned'(regf_mixint_c_int_rbus_i), data_mixint_r_uint_r, unsigned'(data_mixint_r_int_r)};
        end
        10'h00D: begin
          mem_rdata_o = {data_wide_b_r, data_wide_a_r};
        end
        10'h00E: begin
          mem_rdata_o = {data_wide_d_r, data_base_r};
        end
        10'h010: begin
          mem_rdata_o = data_full_f0_r;
        end
        default: begin
          mem_rdata_o = 32'h00000000;
        end
      endcase
    end else begin
      mem_rdata_o = 32'h00000000;
    end
  end

  // ------------------------------------------------------
  //  Output Assignments
  // ------------------------------------------------------
  assign regf_ctrl_ena_rval_o           = data_ctrl_ena_r;
  assign regf_grpa_ctrl_start_rval_o    = data_ctrl_start_r;
  assign regf_grpb_ctrl_start_rval_o    = data_ctrl_start_r;
  assign regf_ctrl_ver_rval_o           = data_ctrl_ver_c;
  assign regf_grpc_ctrl_spec1_rd_o      = bus_ctrl_rden_s;
  assign regf_txdata_bytes_rval_o       = data_txdata_bytes_r;
  assign regf_dims_wrval_rval_o         = data_dims_wrval_r;
  assign regf_dims_wrval_upd_o          = upd_strb_dims_wrval_r;
  assign regf_grpc_dims_spec2_wbus_o[0] = dims_spec2_wbus_s[0];
  assign regf_grpc_dims_spec2_wr_o[0]   = bus_dims_wren_s[0];
  assign regf_grpc_dims_spec2_wbus_o[1] = dims_spec2_wbus_s[1];
  assign regf_grpc_dims_spec2_wr_o[1]   = bus_dims_wren_s[1];
  assign regf_grpc_dims_spec2_wbus_o[2] = dims_spec2_wbus_s[2];
  assign regf_grpc_dims_spec2_wr_o[2]   = bus_dims_wren_s[2];
  assign regf_grpc_dims_spec3_rval_o    = data_dims_spec3_r;
  assign regf_guards_once_rval_o        = data_guards_once_r;
  assign regf_guards_coreonce_wbus_o[0] = guards_coreonce_wbus_s[0];
  assign regf_guards_coreonce_wr_o[0]   = bus_guards_wrguard_1_flg1_wren_s[0];
  assign regf_guards_busonce_wbus_o[0]  = guards_busonce_wbus_s[0];
  assign regf_guards_busonce_wr_o[0]    = bus_guards_wrguard_1_flg1_wren_s[0];
  assign regf_guards_single_rval_o      = data_guards_single_r;
  assign regf_guards_onetime_rval_o     = data_guards_onetime_r;
  assign regf_guards_guard_a_rval_o     = data_guards_guard_a_r;
  assign regf_guards_guard_b_rval_o     = data_guards_guard_b_r;
  assign regf_guards_guard_c_rval_o     = data_guards_guard_c_r;
  assign regf_guards_guard_c_upd_o      = upd_strb_guards_guard_c_r;
  assign regf_guards_cprio_rval_o       = data_guards_cprio_r;
  assign regf_guards_bprio_rval_o       = data_guards_bprio_r;
  assign regf_guards_grdport_rval_o     = data_guards_grdport_r;
  assign regf_grddim_num_wbus_o[0]      = grddim_num_wbus_s[0];
  assign regf_grddim_num_wr_o[0]        = bus_grddim_wrguard_1_wren_s[0];
  assign regf_grddim_num_wbus_o[1]      = grddim_num_wbus_s[1];
  assign regf_grddim_num_wr_o[1]        = bus_grddim_wrguard_1_wren_s[1];
  assign regf_grddim_const_rval_o       = data_grddim_const_c;
  assign regf_grpa_grddim_int_wbus_o[0] = grddim_int_wbus_s[0];
  assign regf_grpa_grddim_int_wr_o[0]   = bus_grddim_wrguard_3_wren_s[0];
  assign regf_grpa_grddim_int_wbus_o[1] = grddim_int_wbus_s[1];
  assign regf_grpa_grddim_int_wr_o[1]   = bus_grddim_wrguard_3_wren_s[1];
  assign regf_mixint_r_int_rval_o       = data_mixint_r_int_r;
  assign regf_mixint_r_uint_rval_o      = data_mixint_r_uint_r;
  assign regf_mixint_c_int_wbus_o       = mixint_c_int_wbus_s;
  assign regf_mixint_c_int_wr_o         = bus_mixint_wren_s;
  assign regf_wide_a_rval_o             = data_wide_a_r;
  assign regf_wide_b_rval_o             = data_wide_b_r;
  assign regf_base_rval_o               = data_base_r;
  assign regf_wide_d_rval_o             = data_wide_d_r;
  assign regf_wonly_wo_rval_o           = data_wonly_wo_r;
  assign regf_full_f0_rval_o            = data_full_f0_r;
  assign regf_full_f0_upd_o             = upd_strb_full_f0_r;

endmodule // corner_regf

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
