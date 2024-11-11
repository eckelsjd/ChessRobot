#define STEPS_PER_REV 200	 // (published)
#define PITCH_DIAMETER 12.73 // (measured)
#define Z_MM_REV 8.11		 // mm/rev (measured)
#define SQUARE_SIZE 57		 // mm
#define Z_HEIGHT 112		 // mm (measured)
#define Y_OFFSET 64.7        // mm (measured)
#define X_OFFSET 65.6        // mm (measured)

// TUNE THESE (SPEEDS)
#define Z_MM_S 20
#define XY_MM_S 180
#define CLAW_REV_S 1
const int claw_steps = 55;

// CALCULATED VALUES
const float z_steps_mm = 1 / (Z_MM_REV / STEPS_PER_REV);
const float xy_steps_mm = STEPS_PER_REV / (PI * PITCH_DIAMETER);
const float z_rev_s = Z_MM_S / Z_MM_REV;
const float xy_rev_s = XY_MM_S / (PI * PITCH_DIAMETER);
const int vertical_steps = floor((Z_HEIGHT / Z_MM_REV) * STEPS_PER_REV);
//const int claw_steps = floor(0.37 * STEPS_PER_REV);

// MOTOR STEP DELAYS (microseconds)
const float z_us_step = 1000000 / (2 * z_rev_s * STEPS_PER_REV); // factor of 2 because 2 delays in single mstep loop
const float xy_us_step = 1000000 / (2 * xy_rev_s * STEPS_PER_REV);
const float claw_us_step = 1000000 / (2 * CLAW_REV_S * STEPS_PER_REV);

// PINS
#define ENABLE 8
#define MX_DIR 5
#define MX_STEP 2
#define MY_DIR 6
#define MY_STEP 3
#define MZ_DIR 7
#define MZ_STEP 4
#define MC_DIR 13 // 52
#define MC_STEP 12 //50
#define X_LIM 9
#define Y_LIM 10
#define Z_LIM 11

// SERIAL
String inputString = "";
bool stringComplete = false;

// GLOBALS
volatile float x_location = 0;
volatile float y_location = 0;
volatile float z_location = 0;
bool play_as_black = true;

void setup()
{
	Serial.begin(9600);
	inputString.reserve(200);

	pinMode(MX_DIR, OUTPUT);
	pinMode(MX_STEP, OUTPUT);
	pinMode(MY_DIR, OUTPUT);
	pinMode(MY_STEP, OUTPUT);
	pinMode(MZ_DIR, OUTPUT);
	pinMode(MZ_STEP, OUTPUT);
	pinMode(MC_DIR, OUTPUT);
	pinMode(MC_STEP, OUTPUT);
	pinMode(ENABLE, OUTPUT);

	pinMode(X_LIM, INPUT_PULLUP);
	pinMode(Y_LIM, INPUT_PULLUP);
	pinMode(Z_LIM, INPUT_PULLUP);

	digitalWrite(ENABLE, HIGH); //disable motors
}

void loop()
{

	if (stringComplete)
	{
		inputString.toUpperCase();
		inputString.trim(); // gets rid of Carriage return CR (ASCII 13)

		if (inputString.startsWith("PICKUP"))
		{
			mstep(MZ_STEP, MZ_DIR, vertical_steps, z_us_step);
			mstep(MC_STEP, MC_DIR, claw_steps, claw_us_step);
			homeZ();
		}
		else if (inputString.startsWith("PUTDOWN"))
		{
			mstep(MZ_STEP, MZ_DIR, vertical_steps, z_us_step);
			mstep(MC_STEP, MC_DIR, -claw_steps, claw_us_step);
			homeZ();
		}
		else if (inputString.startsWith("PLAYAS ")) {
			char play_as = inputString.charAt(7);
			play_as_black = (play_as == 'B');
		}
		else if (inputString.startsWith("ENABLE")) {
			digitalWrite(ENABLE, !digitalRead(ENABLE));
		}
		else if (inputString.startsWith("HOME")) {
			homeZ();
			homeY();
			homeX();
		}
		else if (inputString.startsWith("GO ")) {
			char file;
			int rank; 
			int num_files; //num files away from origin corner square (A8 for black, H1 for white)
			int num_ranks; //num ranks away from origin corner square
			float x_abs;
			float y_abs;

			file = inputString.charAt(3);
			rank = String(inputString.charAt(4)).toInt();

			if (play_as_black) {
				num_files = file - 'A';
				num_ranks = 8 - rank;
			} else { // play as white
				num_files = 'H' - file;
				num_ranks = rank - 1;
			}

			x_abs = X_OFFSET + SQUARE_SIZE*num_files;
			y_abs = Y_OFFSET + SQUARE_SIZE*num_ranks;
			go_to_absolute(x_abs,y_abs);
		}
		else
		{
			// BASIC COMMANDS
			// cmd = Z +100
			char firstChar = inputString.charAt(0);
			char sign = inputString.charAt(2);
			int multiplier = (sign == '+') ? 1 : -1;
			int steps = inputString.substring(3).toInt() * multiplier;
			switch (firstChar)
			{
			case 'C':
				mstep(MC_STEP, MC_DIR, steps, claw_us_step);
				break;
			case 'X':
				mstep(MX_STEP, MX_DIR, steps, xy_us_step);
				x_location += steps/xy_steps_mm;
				break;
			case 'Y':
				mstep(MY_STEP, MY_DIR, steps, xy_us_step);
				y_location += steps/xy_steps_mm;
				break;
			case 'Z':
				mstep(MZ_STEP, MZ_DIR, steps, z_us_step);
				z_location += steps/z_steps_mm;
				break;
			default:
				break;
			}
		}


		Serial.println(String("X: ") + round(x_location) + String(" Y: ") + round(y_location)); // blocks caller until movement is done
		inputString = "";
		stringComplete = false;
	}
}

// go to (x,y) in mm from origin
void go_to_absolute(float x, float y) {
	float delta_x = x - x_location;
	float delta_y = y - y_location;

	if (delta_x < 0) {
		negative_spin(MX_DIR);
	} else { positive_spin(MX_DIR); }
	if (delta_y < 0) {
		negative_spin(MY_DIR);
	} else { positive_spin(MY_DIR); }

	int x_steps = round(abs(delta_x)*xy_steps_mm);
	int y_steps = round(abs(delta_y)*xy_steps_mm);

	while (x_steps || y_steps) {
		if (x_steps > 0) {
			digitalWrite(MX_STEP,HIGH);
			x_steps--;
		}
		if (y_steps > 0) {
			digitalWrite(MY_STEP,HIGH);
			y_steps--;
		}

		delayMicroseconds(xy_us_step);
		digitalWrite(MX_STEP,LOW);
		digitalWrite(MY_STEP,LOW);
		delayMicroseconds(xy_us_step);
	}
	x_location += delta_x;
	y_location += delta_y;
}

void homeX() {
	negative_spin(MX_DIR); // negative homes all 3 axes
	float delay_us = xy_us_step;
	while (digitalRead(X_LIM))
	{
		digitalWrite(MX_STEP, HIGH);
		delayMicroseconds(delay_us);
		digitalWrite(MX_STEP, LOW);
		delayMicroseconds(delay_us);

		x_location -= 1/xy_steps_mm;

		if (x_location < 40) { // slow down 4cm from limit switch
			delay_us = xy_us_step*2;
		}
		if (x_location < 20) {
			delay_us = xy_us_step*2.5;
		}
	}
	positive_spin(MX_DIR);
	while (!digitalRead(X_LIM))
	{
		digitalWrite(MX_STEP, HIGH);
		delayMicroseconds(delay_us);
		digitalWrite(MX_STEP, LOW);
		delayMicroseconds(delay_us);
	}
	x_location = 0;
}

void homeY() {
	negative_spin(MY_DIR); // negative homes all 3 axes
	float delay_us = xy_us_step;
	while (digitalRead(Y_LIM))
	{
		digitalWrite(MY_STEP, HIGH);
		delayMicroseconds(delay_us);
		digitalWrite(MY_STEP, LOW);
		delayMicroseconds(delay_us);

		y_location -= 1/xy_steps_mm;

		if (y_location < 40) { // slow down 2cm from limit switch
			delay_us = xy_us_step*2;
		}
		if (y_location < 20) {
			delay_us = xy_us_step*2.5;
		}
	}
	positive_spin(MY_DIR);
	while (!digitalRead(Y_LIM))
	{
		digitalWrite(MY_STEP, HIGH);
		delayMicroseconds(delay_us);
		digitalWrite(MY_STEP, LOW);
		delayMicroseconds(delay_us);
	}
	y_location = 0;
}

void homeZ() {
	negative_spin(MZ_DIR); // negative homes all 3 axes
	while (digitalRead(Z_LIM))
	{
		digitalWrite(MZ_STEP, HIGH);
		delayMicroseconds(z_us_step);
		digitalWrite(MZ_STEP, LOW);
		delayMicroseconds(z_us_step);

		z_location -= 1/z_steps_mm;
	}
	positive_spin(MZ_DIR);
	while (!digitalRead(Z_LIM))
	{
		digitalWrite(MZ_STEP, HIGH);
		delayMicroseconds(z_us_step);
		digitalWrite(MZ_STEP, LOW);
		delayMicroseconds(z_us_step);
	}
	z_location = 0;
}

// negative for X,Y,Z will home
// negative for claw is opening
void negative_spin(int dir_pin)
{
	digitalWrite(dir_pin, HIGH);
}

// positive X = right
// positive Y = down
// positive Z = down
// positive claw = closing
void positive_spin(int dir_pin)
{
	digitalWrite(dir_pin, LOW);
}

void mstep(int step_pin, int dir_pin, int steps, float delay_us)
{
	if (steps < 0)
	{
		negative_spin(dir_pin);
	}
	else
	{
		positive_spin(dir_pin);
	}

	for (int i = 0; i < abs(steps); i++)
	{
		digitalWrite(step_pin, HIGH);
		delayMicroseconds(delay_us);
		digitalWrite(step_pin, LOW);
		delayMicroseconds(delay_us);
	}
}

void serialEvent()
{
	while (Serial.available())
	{   
		char inChar = (char)Serial.read();
		if (inChar == '\n')
		{ // line feed (ASCII 10)
			stringComplete = true;
		}
		else
		{
			inputString += inChar;
		}
	}
}
