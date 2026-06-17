#include <vector>

using EMBEDDED_FEATURE_TYPE = float;
using EMBEDDED_TARGET_TYPE = float;

#define EMBEDDED_NB_ROWS 16

#define EMBEDDED_NB_FEATURES 11

using tEmbeddedFeatureVector = EMBEDDED_FEATURE_TYPE[ EMBEDDED_NB_FEATURES ];

struct sEMBEDDED_X_Y {
	tEmbeddedFeatureVector X;
	EMBEDDED_TARGET_TYPE y;
};

static const std::vector<sEMBEDDED_X_Y> gEMBEDDED_DATASET {
	{ .X = { Valiant, 6, 225.0, 105, 2.76, 3.46, 20.22, 1, 0, 3, 1 }, .y = 18.1 },
	{ .X = { Datsun 710, 4, 108.0, 93, 3.85, 2.32, 18.61, 1, 1, 4, 1 }, .y = 22.8 },
	{ .X = { Fiat 128, 4, 78.7, 66, 4.08, 2.2, 19.47, 1, 1, 4, 1 }, .y = 32.4 },
	{ .X = { Honda Civic, 4, 75.7, 52, 4.93, 1.615, 18.52, 1, 1, 4, 2 }, .y = 30.4 },
	{ .X = { Merc 450SE, 8, 275.8, 180, 3.07, 4.07, 17.4, 0, 0, 3, 3 }, .y = 16.4 },
	{ .X = { Merc 450SLC, 8, 275.8, 180, 3.07, 3.78, 18.0, 0, 0, 3, 3 }, .y = 15.2 },
	{ .X = { Cadillac Fleetwood, 8, 472.0, 205, 2.93, 5.25, 17.98, 0, 0, 3, 4 }, .y = 10.4 },
	{ .X = { Merc 240D, 4, 146.7, 62, 3.69, 3.19, 20.0, 1, 0, 4, 2 }, .y = 24.4 },
	{ .X = { Maserati Bora, 8, 301.0, 335, 3.54, 3.57, 14.6, 0, 1, 5, 8 }, .y = 15.0 },
	{ .X = { Mazda RX4 Wag, 6, 160.0, 110, 3.9, 2.875, 17.02, 0, 1, 4, 4 }, .y = 21.0 },
	{ .X = { Dodge Challenger, 8, 318.0, 150, 2.76, 3.52, 16.87, 0, 0, 3, 2 }, .y = 15.5 },
	{ .X = { Mazda RX4, 6, 160.0, 110, 3.9, 2.62, 16.46, 0, 1, 4, 4 }, .y = 21.0 },
	{ .X = { AMC Javelin, 8, 304.0, 150, 3.15, 3.435, 17.3, 0, 0, 3, 2 }, .y = 15.2 },
	{ .X = { Porsche 914-2, 4, 120.3, 91, 4.43, 2.14, 16.7, 0, 1, 5, 2 }, .y = 26.0 },
	{ .X = { Merc 280C, 6, 167.6, 123, 3.92, 3.44, 18.9, 1, 0, 4, 4 }, .y = 17.8 },
	{ .X = { Merc 230, 4, 140.8, 95, 3.92, 3.15, 22.9, 1, 0, 4, 2 }, .y = 22.8 }
}; // eof gEMBEDDED_DATASET
