# Instrument management bus: protocol draft

Status: proposed. A possible future protocol for custom domain controllers; not decided and not scheduled. Today all slow-control devices, including the first custom boards, use Modbus RTU ([ADR-014](../adr/ADR-014_slow_control_domains_and_transports.md)). Requirement IDs `IMB-NNN` apply only if this protocol is adopted.

**Document ID:** IMB-SPEC

**Version:** 0.1 (draft)

**Target Platform:** Embedded Linux (System Controller) & Zephyr RTOS (Domain Controllers)

**Target Application:** Cosmic-Ray Muon Instrumentation Platform

**Physical Topology:** RS-485 port(s) dedicated to IMB nodes inside the cabinet ($1\,\text{m}\times 1\,\text{m}\times 1\,\text{m}$ instrument cabinet)

---

## 1. System Overview

This specification defines the system requirements and firmware/software architecture for an intra-cabinet instrument management bus (IMB) deployed within a high-precision **cosmic-ray muon instrumentation platform** (e.g., TBM tunnel survey payloads, structural health monitoring, or geological field units).

The baseline physics and link layer is based on RS-485 serial bus.
The system described in this document decouples upper-layer Linux applications from physical hardware details using a **Centralized Serial Gateway Daemon** on the System Controller and **Remote Procedure Call (RPC) domain abstractions** over COBS (Consistent Overhead Byte Stuffing) and Protobuf on Zephyr-based Domain Controllers.

The architecture natively supports multi-tenant operation, handling **multiple distinct domain types** (e.g., High-Voltage Bias, Gas-Supply Control, Environmental/IMU Sensors) as well as **multiple instances of the same domain type** (e.g., HV Board #1, HV Board #2) on one RS-485 port without hardware port sprawl or register-level leakages.

```
+---------------------------------------------------------------------------------------------------+
|                                 SYSTEM CONTROLLER (Linux)                                         |
|                                                                                                   |
|   +-----------------------+   +-----------------------+   +-----------------------+               |
|   | Domain Service Client |   | Domain Service Client |   | External Client (gRPC)|               |
|   +-----------------------+   +-----------------------+   +-----------------------+               |
|               │                           │                           │                           |
|               └───────────────────────────┼───────────────────────────┘                           |
|                                           │ Domain API / IPC (Target: domain_type + instance_id)  |
|                                           ▼                                                       |
|   +-------------------------------------------------------------------------------------------+   |
|   |                         RS-485 SERIAL GATEWAY DAEMON                                      |   |
|   |  - Owns /dev/ttyS1 exclusively                                                            |   |
|   |  - Dynamic Board Registry (Maps "power_domain:2" -> Node 0x0B)                            |   |
|   |  - High-Speed Async Frame Priority Queue & Serial Mutex                                   |   |
|   |  - ZERO knowledge of Domain Registers or Domain-Specific Business Logic                   |   |
|   +-------------------------------------------------------------------------------------------+   |
|                                           │ Serial Port (/dev/ttyS1 @ 921.6k - 1.5M baud)         |
+-------------------------------------------┼-------------------------------------------------------+
                                            │ RS-485 port dedicated to IMB
        ┌───────────────────────────────────┼───────────────────────────────────┐
        ▼                                   ▼                                   ▼
+───────────────────────────+   +───────────────────────────+   +───────────────────────────+
| Node 0x0A                 |   | Node 0x0B                 |   | Node 0x30                 |
| - Domain: "hv_domain"     |   | - Domain: "hv_domain"     |   | - Domain: "gas_domain"    |
| - Instance ID: 1          |   | - Instance ID: 2          |   | - Instance ID: 1          |
| - Zephyr RTOS + Nanopb    |   | - Zephyr RTOS + Nanopb    |   | - Zephyr RTOS + Nanopb    |
+───────────────────────────+   +───────────────────────────+   +───────────────────────────+

```

---

## 2. System Requirements

### 2.1 Functional Requirements

* **[IMB-001] Bus Ownership Isolation:** The Linux Serial Gateway Daemon shall be the sole process with read/write access to the host physical serial interface (`/dev/ttyS1` or equivalent).
* **[IMB-002] Domain API Abstraction:** Domain controllers shall expose strong-typed RPC methods (e.g., `SetVoltage`, `SetFlow`). Raw register offsets and memory-mapped address layouts shall **not** be exposed to upper-layer Linux host software.
* **[IMB-003] Multi-Client Concurrent Access:** The Gateway Daemon shall accept concurrent IPC requests from multiple host-side service clients, multiplexing their requests transparently onto the half-duplex bus.
* **[IMB-004] Dynamic Node Discovery & Addressing:** The Gateway Daemon shall maintain a dynamic board registry mapping abstract logical endpoints (`domain_type` + `instance_id`) to physical wire addresses (`node_id`). Host applications shall invoke services using logical identity rather than physical node addresses.
* **[IMB-005] Multi-Instance Support:** The architecture shall support multiple physical boards sharing the exact same domain type and firmware on the same bus without address collisions or service ambiguity.

### 2.2 Non-Functional Requirements

* **[IMB-101] Physical Cable Length:** The physical bus wire length shall not exceed $2.0\,\text{m}$ (enclosed strictly within the $1\,\text{m}^3$ cabinet).
* **[IMB-102] Baud Rate & Throughput:** The serial bus shall operate at a configurable baud rate between **921,600 bps** and **1,500,000 bps (1.5 Mbps)**.
* **[IMB-103] Message Overhead & Latency:** Total frame processing overhead on the gateway daemon shall be less than $1.0\,\text{ms}$. Round-trip execution for standard control commands shall not exceed $10.0\,\text{ms}$.
* **[IMB-104] Frame Framing & Integrity:** Every packet transmitted across the wire shall be framed with COBS using `0x00` delimiters and protected by a **CRC-16-CCITT** checksum.

---

## 3. Bus Frame & Message Specification

### 3.1 Wire Envelope Format

All physical RS-485 frames adhere to a unified transport envelope byte-stuffed using COBS so that `0x00` exclusively serves as the frame delimiter.

$$\text{[ 0x00 Delimiter ] [ COBS-Encoded Transport Payload ] [ 0x00 Delimiter ]}$$

#### Unencoded Transport Payload Structure

| Field | Size (Bytes) | Description |
| --- | --- | --- |
| **`target_node_id`** | 1 | Destination Physical Address ($0\text{x}01 - 0\text{x}FE$; $0\text{x}FF$ = Broadcast, $0\text{x}00$ = Host) |
| **`source_node_id`** | 1 | Sender Physical Address |
| **`sequence_number`** | 2 | Message Sequence Counter (uint16) for ACK matching and frame tracking |
| **`msg_type`** | 1 | `0x01` = RPC Request, `0x02` = RPC Response, `0x03` = Discovery/Ping, `0x04` = Async Alert |
| **`payload_len`** | 2 | Length of the Protobuf Payload (uint16) |
| **`protobuf_payload`** | $N$ | Serialized Nanopb / Protobuf RPC binary message |
| **`crc16`** | 2 | CRC-16-CCITT over all preceding fields in this header + payload |

---

### 3.2 Protocol Buffer Interface (.proto) Definition

System management and domain APIs are defined using Protocol Buffers v3.

```protobuf
syntax = "proto3";

package domain_rpc;

// ============================================================================
// Core System Messages (Service ID: 0-99)
// ============================================================================

message PingRequest {}

message PingResponse {
  uint32 node_id       = 1;  // Physical address (e.g., 0x0A)
  string domain_type   = 2;  // e.g., "hv_domain", "gas_domain"
  uint32 instance_id   = 3;  // e.g., 1, 2, 3 (Board instance index)
  string hardware_uid  = 4;  // MCU 128-bit unique hardware ID
  string fw_version    = 5;  // Firmware version "1.2.0"
}

// ============================================================================
// Generic RPC Envelopes
// ============================================================================

message BusRequest {
  uint32 service_id = 1;     // e.g., 100 = HV Domain, 200 = DAQ Domain
  uint32 method_id  = 2;     // e.g., 1 = SetVoltage, 2 = GetCountRate
  bytes  payload    = 3;     // Serialized method argument struct
}

message BusResponse {
  uint32 status_code = 1;    // 0 = SUCCESS, 1 = INVALID_METHOD, 2 = HARDWARE_ERROR
  bytes  payload     = 2;    // Serialized return struct
}

// ============================================================================
// Domain Specific Payload Schemas (Service ID: 100+)
// ============================================================================

// Service ID 100: High Voltage Bias Domain
message SetVoltageReq {
  uint32 channel_id  = 1;
  float  target_volts = 2;
}

message SetVoltageResp {
  float  actual_volts = 1;
}

```

---

## 4. Addressing, Discovery & Multi-Instance Routing Strategy

### 4.1 Physical Node Identification

Each physical board on the RS-485 bus is assigned a unique 8-bit `node_id` ($0\text{x}01$ through $0\text{x}FE$). On Zephyr domain boards, the physical `node_id` is assigned via hardware (DIP switches / resistor strapping), stored in Non-Volatile Storage (`CONFIG_NVS`), or dynamically bound during discovery.

### 4.2 Board Discovery & Registry Table

At boot, the Linux Gateway Daemon broadcasts a `PingRequest` (or polls node range $0\text{x}01 - 0\text{x}FE$). Each online board responds with its physical `node_id`, its `domain_type`, and its `instance_id`.

The Gateway Daemon populates an internal **Routing Table**:

| Physical `node_id` | `domain_type` | `instance_id` | Hardware Serial / UID | Logical Endpoint |
| --- | --- | --- | --- | --- |
| `0x0A` | `hv_domain` | `1` | `STM32F4-98A1...` | `/services/hv/1` |
| `0x0B` | `hv_domain` | `2` | `STM32F4-98A2...` | `/services/hv/2` |
| `0x20` | `sensor_domain` | `1` | `STM32F4-77C1...` | `/services/sensor/1` |
| `0x30` | `gas_domain` | `1` | `STM32F4-33B1...` | `/services/gas/1` |

### 4.3 Host Client Routing Workflow

1. **Targeted Dispatch:** An upper-layer client issues a request to `("hv_domain", instance_id = 2)`.
2. **Address Resolution:** Gateway Daemon checks its routing table and resolves `("hv_domain", 2)` $\rightarrow$ `node_id = 0x0B`.
3. **Bus Execution:** The daemon frames the Protobuf RPC payload inside a transport envelope with `target_node_id = 0x0B`, sends it over the wire, and returns the response asynchronously to the client.

---

## 5. Linux Gateway Daemon Architecture

The Linux daemon manages `/dev/ttyS1`, executes RS-485 driver ioctls, handles local client connections via Unix Sockets, and routes incoming/outgoing frames.

```
                     ┌────────────────────────────────┐
                     │    Linux Domain API Client     │
                     └───────────────┬────────────────┘
                                     │ Unix Domain Socket / IPC
                                     │ (Target: "hv_domain", Instance: 2)
                                     ▼
                     ┌────────────────────────────────┐
                     │       IPC Server Thread        │
                     └───────────────┬────────────────┘
                                     │ Resolve Target & Enqueue
                                     ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        GATEWAY DAEMON CORE                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │   In-Memory Board Registry Table & Resolution Engine            │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │   Priority Request Queue (Thread-Safe Queue)                    │  │
│  └─────────────────────────────┬───────────────────────────────────┘  │
│                                │                                      │
│                                ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │               RS-485 Bus Master Worker Thread                   │  │
│  │  - Serial Port IO Lock                                          │  │
│  │  - COBS Encode/Decode & CRC Verification                        │  │
│  │  - Timeout & Retry Logic                                        │  │
│  └─────────────────────────────┬───────────────────────────────────┘  │
└────────────────────────────────┼──────────────────────────────────────┘
                                 │ POSIX termios2 / TIOCSRS485
                                 ▼
                     ┌────────────────────────────────┐
                     │      /dev/ttyS1 (RS-485)       │
                     └────────────────────────────────┘

```

### 5.1 Linux Hardware Configuration Code Example

```c
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/serial.h>
#include <termios.h>

int configure_rs485_port(const char* device_path, int baud_rate) {
    int fd = open(device_path, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) return -1;

    // Configure Kernel Hardware RTS Direction Toggling
    struct serial_rs485 rs485conf = {0};
    rs485conf.flags |= SER_RS485_ENABLED;
    rs485conf.flags |= SER_RS485_RTS_ON_SEND;       // Drive DE high during TX
    rs485conf.flags &= ~SER_RS485_RTS_AFTER_SEND;   // Drop DE low after TX
    rs485conf.delay_rts_before_send = 0;
    rs485conf.delay_rts_after_send = 0;

    if (ioctl(fd, TIOCSRS485, &rs485conf) < 0) {
        close(fd);
        return -2;
    }

    // Configure Raw Mode & High Baud Rate (e.g., 921,600 or 1,500,000)
    struct termios options;
    tcgetattr(fd, &options);
    cfmakeraw(&options);
    
    cfsetispeed(&options, B921600);
    cfsetospeed(&options, B921600);

    options.c_cflag |= (CLOCAL | CREAD);
    options.c_cflag &= ~PARENB; // No parity
    options.c_cflag &= ~CSTOPB; // 1 stop bit
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;      // 8 data bits

    tcsetattr(fd, TCSANOW, &options);
    return fd;
}

```

---

## 6. Zephyr RTOS Domain Controller Firmware Design

Zephyr domain controllers use native asynchronous UART drivers, hardware-driven DE/RE toggling, and Nanopb for RPC decoding.

```
                           Incoming COBS Frame
                                    │
                                    ▼
                   ┌─────────────────────────────────┐
                   │    Zephyr Bus Receiver Task     │
                   └────────────────┬────────────────┘
                                    │
                                    ▼
                   ┌─────────────────────────────────┐
                   │  Base System Service Handler    │
                   │  (Responds to Ping / Discovery) │
                   └────────────────┬────────────────┘
                                    │
                                    ▼
                   ┌─────────────────────────────────┐
                   │  Domain RPC Service Dispatcher  │
                   └────────────────┬────────────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             ▼                      ▼                      ▼
┌────────────────────────┐┌───────────────────┐┌───────────────────┐
│  HV Domain Handler     ││ DAQ Domain Handler││Sensor Domain Handl│
│ (Active on HV FW)      ││ (Active on DAQ FW)││(Active on Sensor) │
└────────────────────────┘└───────────────────┘└───────────────────┘

```

### 6.1 Zephyr Devicetree (`app.overlay`) & Kconfig (`prj.conf`)

```dts
/* app.overlay */
&usart1 {
    status = "okay";
    current-speed = <921600>;
    pinctrl-0 = <&usart1_tx_default &usart1_rx_default>;
    pinctrl-names = "default";

    rs485-rts-active-high;
    de-gpios = <&gpioa 12 GPIO_ACTIVE_HIGH>;
};

```

```ini
# prj.conf
CONFIG_SERIAL=y
CONFIG_UART_ASYNC_API=y
CONFIG_GPIO=y
CONFIG_COBS=y
CONFIG_CRC=y
CONFIG_HEAP_MEM_POOL_SIZE=4096

```

### 6.2 Zephyr Dispatcher & Multi-Domain Implementation

```c
#include <zephyr/kernel.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/sys/cobs.h>
#include <zephyr/sys/crc.h>
#include <pb_decode.h>
#include <pb_encode.h>
#include "domain_rpc.pb.h"

// Set at boot via hardware switches, NVS, or build flags
static uint8_t g_node_id = CONFIG_APP_NODE_ID;               // e.g., 0x0B
static uint32_t g_instance_id = CONFIG_APP_INSTANCE_ID;       // e.g., 2
static const char* g_domain_type = CONFIG_APP_DOMAIN_TYPE;   // "hv_domain"

// 1. Core System Call Handler (Common across all boards)
bool handle_system_service(uint32_t method_id, const pb_istream_t *stream) {
    if (method_id == 1) { // Ping / Discovery
        domain_rpc_PingResponse resp = domain_rpc_PingResponse_init_zero;
        resp.node_id = g_node_id;
        resp.instance_id = g_instance_id;
        strncpy(resp.domain_type, g_domain_type, sizeof(resp.domain_type));
        
        // Encode and transmit response frame back to host (0x00)...
        return true;
    }
    return false;
}

// 2. Main RX Packet Processing Entry Point
void process_incoming_frame(uint8_t target_id, uint8_t *payload_bytes, size_t len) {
    if (target_id != g_node_id && target_id != 0xFF) {
        return; // Filter out packets meant for other boards
    }

    domain_rpc_BusRequest request = domain_rpc_BusRequest_init_zero;
    pb_istream_t stream = pb_istream_from_buffer(payload_bytes, len);

    if (!pb_decode(&stream, domain_rpc_BusRequest_fields, &request)) {
        return;
    }

    // Route System Calls
    if (request.service_id < 100) {
        pb_istream_t payload_stream = pb_istream_from_buffer(request.payload.bytes, request.payload.size);
        handle_system_service(request.method_id, &payload_stream);
        return;
    }

    // Route Application Domain Calls
    #if defined(CONFIG_APP_IS_HV_DOMAIN)
    if (request.service_id == 100) {
        // hv_domain_dispatch(request.method_id, &payload_stream);
    }
    #elif defined(CONFIG_APP_IS_GAS_DOMAIN)
    if (request.service_id == 200) {
        // gas_domain_dispatch(request.method_id, &payload_stream);
    }
    #endif
}

```

---

## 7. Verification & Test Matrix

| Test Case | Procedure | Expected Result | Pass/Fail Criteria |
| --- | --- | --- | --- |
| **TC-01: Multi-Instance Addressing** | Connect two identical HV Boards (`instance_id` 1 and 2) to the bus. Issue `SetVoltage` specifically to Instance 2. | Gateway Daemon resolves Instance 2 to `0x0B`. Instance 2 executes command; Instance 1 (`0x0A`) ignores packet. | Verified via serial tracing and logic analyzer. |
| **TC-02: Multi-Client Bus Access** | Fire 100 concurrent RPC calls from 3 independent Linux processes targeting different domain boards. | Gateway Daemon queues and executes all calls sequentially over RS-485. | 0 lost packets, 0 CRC errors, 100% ACK completion. |
| **TC-03: Dynamic Discovery Scan** | Trigger bus discovery scan on Linux daemon with 4 mixed boards connected. | Daemon populates registry table within $< 50\,\text{ms}$ listing all board IDs, domain types, and instances. | All 4 boards correctly registered. |
| **TC-04: Throughput & Latency** | Set baud rate to **921,600 bps**; execute 1,000 round-trip RPC calls across 3 domains. | Average round-trip execution latency remains $< 3.5\,\text{ms}$. | Measured latency $\le 3.5\,\text{ms}$. |

---

## 8. Selection Rationale for Muon Instrumentation Platforms

For field-deployable cosmic-ray muography payloads (e.g., in active subway TBM tunnels, dam seepage monitoring, or remote geological survey cabinets), **COBS + Nanopb Protobuf RPC over RS-485** was selected as the baseline architecture over standard industrial alternatives based on the following domain criteria:

### 8.1 Domain-Specific Evaluation

1. **Multi-Subsystem Heterogeneity:** Muon detectors combine vastly different subsystems—High Voltage bias ramping ($0-3000\,\text{V}$), FPGA trigger/coincidence DAQ, environmental pressure/temperature monitoring, and 6-axis IMUs for geometric vector alignment. Strongly-typed Protobuf schemas (`.proto`) expose expressive domain APIs (`SetHV(channel, volts)`, `ReadBarometer()`) without forcing data into arbitrary 16-bit register tables or rigid CANopen Object Dictionaries.
2. **Noise Immunity in Heavy Industrial EMI Environments:** Active construction environments (e.g., TBM cutterhead motors, high-power inverters) generate severe electrical noise. COBS byte-stuffing provides unambiguous frame boundary identification via `0x00` delimiters, ensuring corrupted noise frames are cleanly dropped via CRC-16 without causing UART state-machine locks or timeout stalls.
3. **Low Latency for Telemetry & Control:** At $921.6\,\text{kbps} - 1.5\,\text{Mbps}$, Nanopb binary encoding achieves round-trip execution latencies of **$< 3.5\,\text{ms}$**, easily handling rapid slow-control parameter adjustments and event-rate monitoring.
4. **Minimal MCU Memory Resource Footprint:** Nanopb and COBS decoding compile into **$< 4\,\text{KB}$ Flash and $1\,\text{KB}$ RAM** on Zephyr RTOS domain microcontrollers, preserving maximum SRAM/Flash for high-frequency hardware interrupt handlers, ADC buffer DMA, and coincidental trigger processing.

---

## 9. Alternative RS-485 Protocol Comparison

While the baseline specification relies on **COBS + Nanopb Protobuf RPC**, alternative standard protocols running over RS-485 were evaluated during initial trade studies.

### 9.1 Evaluated Standard Protocols

* **CANopen over Serial (CiA 309-3):** Encapsulates CANopen Object Dictionaries (SDO/PDO) over serial lines. Exposes structured memory indexes, but introduces high parsing overhead relative to Nanopb and rigid data modeling.
* **BACnet MS/TP:** Utilizes software token-passing for multi-master access over RS-485. Evaluated and rejected due to token rotation latency jitter, which degrades real-time responsiveness during calibration or HV fault events.
* **PROFIBUS DP:** High-speed industrial fieldbus ($12\,\text{Mbps}$). Rejected due to excessive stack complexity, licensing friction, and reliance on dedicated hardware ASICs on domain microcontrollers.
* **SLIP / CoAP (IP over Serial):** Runs Point-to-Point framing to assign IPv4/IPv6 addresses directly to domain controllers. Evaluated as an alternative for pure IP-native environments, but rejected for the primary baseline due to full TCP/IP or UDP socket memory overhead on low-power domain MCUs.

### 9.2 Trade-Off Matrix

| Protocol | Topology | Multi-Master Support | Data / Service Abstraction | Zephyr Memory Footprint | Recommendation |
| --- | --- | --- | --- | --- | --- |
| **COBS + Protobuf RPC (Selected Baseline)** | Master-Slave + Alert | Via Host Gateway | Strong-Typed Protobuf RPC | **Minimal (< 4 KB)** | **Selected Baseline:** Optimal performance, zero register leakage, minimal footprint. |
| **CANopen over Serial (CiA 309-3)** | Peer-to-Peer / Master-Slave | SDO / PDO Events | Standard Object Dictionary | Medium (~12 KB) | **Alternative:** Suitable if standard industrial fieldbus tooling is mandatory. |
| **BACnet MS/TP** | Token-Passing | Native Token | Abstract Named Objects | Large (~30 KB) | **Not Recommended:** Unnecessary token rotation overhead in short cabinets. |
| **PROFIBUS DP** | Token + Master-Slave | Native Hybrid | Cyclic I/O Buffers | Large / Requires ASIC | **Not Recommended:** Excessive complexity and licensing overhead. |
| **SLIP / CoAP (IP over Serial)** | IP Network | Native UDP / IP | CoAP REST / Protobuf | Medium (~16 KB) | **Alternative:** High architectural elegance if IP-native socket access is required on all boards. |

---

## 10. Future Hardware Iteration Roadmap: CAN-FD Migration

For next-generation hardware revisions of the muon instrument platform, transitioning the physical communication layer from RS-485 transceivers to **CAN-FD (Controller Area Network Flexible Data-Rate)** represents the planned evolution path.

### 10.1 Technical Advantages of CAN-FD

```
                    RS-485 Architecture                      CAN-FD Architecture
             (Requires Master/Daemon Arbitration)         (Hardware Multi-Master)

               +-----------------------+                +-----------------------+
               | Linux Host (Master)   |                | Linux Host (Node 0)   |
               +-----------┬-----------+                +-----------┬-----------+
                           │                                        │
             Shared RS-485 │ Bus                                    │ CAN-FD Bus
       +───────────────────┼───────────────────+      +─────────────┴─────────────+
       │ (Polling/Software │ Arbitration)      │      │ (Hardware Non-Destructive │ Arbitration)
       ▼                   ▼                   ▼      ▼                           ▼
+─────────────+     +─────────────+     +─────────────+ +─────────────+     +─────────────+
| Board 1     |     | Board 2     |     | Board 3     | | Board 1     |     | Board 2     |
| (HV Bias)   |     | (FPGA DAQ)  |     | (Sensors)   | | (HV Bias)   |     | (FPGA DAQ)  |
+─────────────+     +─────────────+     +─────────────+ +─────────────+     +─────────────+

```

1. **Hardware-Level Multi-Master Arbitration (CSMA/CR):** Eliminates software polling bottlenecks and physical daemon arbitration locks. Any board (e.g., an FPGA trigger board during a high-flux cosmic shower or an HV board experiencing a trip) transmits immediately. High-priority frames win bus arbitration automatically without corrupting packets.
2. **Payload Expansion & Acceleration:** CAN-FD increases data payload sizes from 8 bytes to **64 bytes per frame**, operating at $500\,\text{kbps}$ nominal / $2-5\,\text{Mbps}$ data phase. Small-to-medium Protobuf RPC structures fit into a single native CAN-FD frame without multi-packet segmentation.
3. **Native Linux SocketCAN Integration:** Linux natively supports CAN via the **SocketCAN** kernel subsystem (`can0`). Host applications open standard POSIX network sockets (`socket(PF_CAN, SOCK_RAW, CAN_RAW)`), completely eliminating the need for custom Linux serial gateway multiplexer daemons.
4. **Preservation of Firmware Investments:** Protobuf RPC schemas and Nanopb dispatch logic remain **100% identical**. Only the underlying transport layer changes (from COBS over UART to SocketCAN / Zephyr CAN drivers).

### 10.2 Hardware & Firmware Migration Plan

When executing the PCB hardware spin for the next-generation instrument cabinet:

* **Microcontrollers:** Upgrade domain controller MCUs to variants featuring integrated CAN-FD peripherals (e.g., STM32G4, STM32H7, or RP2350).
* **Physical Transceivers:** Replace RS-485 transceivers (e.g., MAX3485) with pin-compatible automotive-grade CAN-FD transceivers (e.g., **TCAN1042** or **TJA1044GT**).
* **Bus Termination:** Retain $120\,\Omega$ split termination resistors at the physical boundaries of the intra-cabinet bus.
* **Address Header Mapping:** Map routing headers directly into 29-bit Extended CAN IDs:

$$\text{[ Priority (3 bits) ] [ Service ID (8 bits) ] [ Source Node ID (8 bits) ] [ Target Node ID (8 bits) ]}$$