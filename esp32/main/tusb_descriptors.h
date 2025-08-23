#ifndef _TUSB_DESCRIPTORS_H_
#define _TUSB_DESCRIPTORS_H_

#include "tusb.h"

static const tusb_desc_device_t desc_device = {
    .bLength            = 18,
    .bDescriptorType    = 1,
    .bcdUSB             = 2.00,
    .bDeviceClass       = 0,
    .bDeviceSubClass    = 0,
    .bDeviceProtocol    = 0,
    .bMaxPacketSize0    = 64,
    .idVendor           = 0x222a,
    .idProduct          = 0x0001,
    .bcdDevice          = 0.00,
    .iManufacturer      = 1,
    .iProduct           = 2,
    .iSerialNumber      = 3,
    .bNumConfigurations = 1
};

static const uint8_t touch_report_desc[] = {
    0x05, 0x0D,        // Usage Page (Digitizer)
    0x09, 0x04,        // Usage (Touch Screen)
    0xA1, 0x01,        // Collection (Application)
    0x09, 0x22,        //   Usage (Finger)
    0xA1, 0x02,        //   Collection (Logical)
    0x09, 0x42,        //     Usage (Tip Switch)
    0x15, 0x00,        //     Logical Minimum (0)
    0x25, 0x01,        //     Logical Maximum (1)
    0x75, 0x01,        //     Report Size (1)
    0x95, 0x01,        //     Report Count (1)
    0x81, 0x02,        //     Input (Data,Var,Abs)
    0x95, 0x07,        //     Report Count (7)
    0x81, 0x03,        //     Input (Cnst,Var,Abs)
    0x05, 0x01,        //     Usage Page (Generic Desktop)
    0x09, 0x30,        //     Usage (X)
    0x26, 0xFF, 0x7F,  //     Logical Maximum (32767)
    0x75, 0x10,        //     Report Size (16)
    0x95, 0x01,        //     Report Count (1)
    0x81, 0x02,        //     Input (Data,Var,Abs)
    0x09, 0x31,        //     Usage (Y)
    0x81, 0x02,        //     Input (Data,Var,Abs)
    0xC0,              //   End Collection
    0xC0               // End Collection
};

// Placeholder for the 107-byte "other" HID report descriptor.
static const uint8_t other_hid_report_desc[] = {
    0x06, 0x00, 0xFF,  // Usage Page (Vendor Defined)
    0x09, 0x01,        // Usage (Vendor Usage 1)
    0xA1, 0x01,        // Collection (Application)
    0x09, 0x02,        //   Usage (Vendor Usage 2)
    0x15, 0x00,        //   Logical Minimum (0)
    0x26, 0xFF, 0x00,  //   Logical Maximum (255)
    0x75, 0x08,        //   Report Size (8)
    0x95, 0x40,        //   Report Count (64)
    0x81, 0x02,        //   Input (Data,Var,Abs)
    0xC0               // End Collection
};

static const char* desc_string[] = {
    (const char[]) { 0x09, 0x04 }, // 0: Language (English)
    "ILITEK",                      // 1: Manufacturer
    "ILITEK-TP",                   // 2: Product
    "V06.00.00.00",                // 3: Serial
};

#define CONFIG_TOTAL_LEN    0x3B

enum {
    ITF_NUM_HID_TOUCH,
    ITF_NUM_HID_OTHER,
    ITF_NUM_TOTAL
};

#define EPNUM_HID_TOUCH     0x82
#define EPNUM_HID_OTHER     0x81

static const uint8_t desc_configuration[] = {
    TUD_CONFIG_DESCRIPTOR(1, ITF_NUM_TOTAL, 0, CONFIG_TOTAL_LEN, 0xA0, 200),
    // Use sizeof() to report the TRUE size of the descriptors
    TUD_HID_DESCRIPTOR(ITF_NUM_HID_TOUCH, 0, HID_ITF_PROTOCOL_NONE, sizeof(touch_report_desc), EPNUM_HID_TOUCH, 64, 1),
    TUD_HID_DESCRIPTOR(ITF_NUM_HID_OTHER, 0, HID_ITF_PROTOCOL_NONE, sizeof(other_hid_report_desc), EPNUM_HID_OTHER, 64, 1)
};

#endif // _TUSB_DESCRIPTORS_H_
