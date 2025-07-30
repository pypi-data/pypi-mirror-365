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
// Module:     bit_en_bit_en2
// Data Model: RegfMod
//             tests/test_svmako.py
//
//
// Addressing-Width: data
// Size:             1024x32 (4 KB)
//
//
// Offset       Word     Field    Bus/Core    Reset    Const    Impl
// dec / hex
// -----------  -------  -------  ----------  -------  -------  ------
// 0 / 0        w0
//              [12:0]   .f0      RW/RO       0x0      False    regf
//              [15:13]  .f1      RW/RO       0x0      False    regf
//              [28:16]  .f2      WO/RO       0x0      False    core
//              [31:29]  .f3      RO/RW       0x0      False    core
//
//
// Mnemonic    ReadOp    WriteOp
// ----------  --------  ---------
// RO          Read
// RW          Read      Write
// WO                    Write
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module bit_en_bit_en2 (
  // main_i: Clock and Reset
  input  wire         main_clk_i,        // Clock
  input  wire         main_rst_an_i,     // Async Reset (Low-Active)
  // mem_i
  input  wire         mem_ena_i,         // Memory Access Enable
  input  wire  [9:0]  mem_addr_i,        // Memory Address
  input  wire         mem_wena_i,        // Memory Write Enable
  input  wire  [31:0] mem_wdata_i,       // Memory Write Data
  output logic [31:0] mem_rdata_o,       // Memory Read Data
  input  wire  [31:0] mem_sel_i,         // Slice Selects
  output logic        mem_err_o,         // Memory Access Failed.
  // regf_o
  //   regf_w0_f0_o: bus=RW core=RO in_regf=True
  output logic [12:0] regf_w0_f0_rval_o, // Core Read Value
  //   regf_w0_f1_o: bus=RW core=RO in_regf=True
  output logic [2:0]  regf_w0_f1_rval_o, // Core Read Value
  //   regf_w0_f2_o: bus=WO core=RO in_regf=False
  output logic [12:0] regf_w0_f2_wbus_o, // Bus Write Value
  output logic [12:0] regf_w0_f2_wr_o,   // Bus Bit-Write Strobe
  //   regf_w0_f3_o: bus=RO core=RW in_regf=False
  input  wire  [2:0]  regf_w0_f3_rbus_i  // Bus Read Value
  // regfword_o
);




  // ------------------------------------------------------
  //  Signals
  // ------------------------------------------------------
  logic [31:0] bit_en_s;
  logic [12:0] data_w0_f0_r;  // Word w0
  logic [2:0]  data_w0_f1_r;
  logic        bus_w0_wren_s; // bus word write enables
  logic [12:0] w0_f2_wbus_s;  // intermediate signals for bus-writes to in-core fields

  // ------------------------------------------------------
  // address decoding
  // ------------------------------------------------------
  always_comb begin: proc_bus_addr_dec
    // defaults
    mem_err_o = 1'b0;
    bus_w0_wren_s = 1'b0;

    // decode address
    if (mem_ena_i == 1'b1) begin
      case (mem_addr_i)
        10'h000: begin
          bus_w0_wren_s = mem_wena_i;
        end
        default: begin
          mem_err_o = 1'b1;
        end
      endcase
    end

    bit_en_s = mem_sel_i;
  end

  // ------------------------------------------------------
  // in-regf storage
  // ------------------------------------------------------
  always_ff @ (posedge main_clk_i or negedge main_rst_an_i) begin: proc_regf_flops
    if (main_rst_an_i == 1'b0) begin
      // Word: w0
      data_w0_f0_r <= 13'h0000;
      data_w0_f1_r <= 3'h0;
    end else begin
      if (bus_w0_wren_s == 1'b1) begin
        data_w0_f0_r <= (data_w0_f0_r & ~bit_en_s[12:0]) | (mem_wdata_i[12:0] & bit_en_s[12:0]);
      end
      if (bus_w0_wren_s == 1'b1) begin
        data_w0_f1_r <= (data_w0_f1_r & ~bit_en_s[15:13]) | (mem_wdata_i[15:13] & bit_en_s[15:13]);
      end
    end
  end

  // ------------------------------------------------------
  // intermediate signals for in-core bus-writes
  // ------------------------------------------------------
  assign w0_f2_wbus_s = bus_w0_wren_s ? mem_wdata_i[28:16] : 13'h0000;

  // ------------------------------------------------------
  //  Bus Read-Mux
  // ------------------------------------------------------
  always_comb begin: proc_bus_rd
    if ((mem_ena_i == 1'b1) && (mem_wena_i == 1'b0)) begin
      case (mem_addr_i)
        10'h000: begin
          mem_rdata_o = {regf_w0_f3_rbus_i, 13'h0000, data_w0_f1_r, data_w0_f0_r};
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
  assign regf_w0_f0_rval_o = data_w0_f0_r;
  assign regf_w0_f1_rval_o = data_w0_f1_r;
  assign regf_w0_f2_wbus_o = w0_f2_wbus_s;
  assign regf_w0_f2_wr_o   =  bus_w0_wren_s ? bit_en_s[28:16] : 13'h0000;

endmodule // bit_en_bit_en2

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
