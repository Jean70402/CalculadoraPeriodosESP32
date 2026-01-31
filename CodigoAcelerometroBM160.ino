#include <BMI160Gen.h>
#include <Wire.h>

const int i2c_addr = 0x68;
const int sda_pin = 6; 
const int scl_pin = 7; 
bool activo = false;

// Variables para el control de tiempo
unsigned long previousMillis = 0;
const long interval = 10; // 10ms = 100Hz

void setup() {
  Serial.begin(921600);
  delay(2000); 

  Wire.begin(sda_pin, scl_pin);

  if (!BMI160.begin(BMI160GenClass::I2C_MODE, i2c_addr)) {
    while (1); 
  }

  BMI160.setAccelerometerRange(2); 
  BMI160.setGyroRange(250);

  // --- BLOQUE DE AUTENTICACIÓN (No tocar, es vital para tu Python) ---
  Serial.println("SISTEMA_EN_ESPERA");
  
  while (!activo) {
    if (Serial.available() > 0) {
      String password = Serial.readStringUntil('\n');
      password.trim(); 

      if (password == "INICIAR") {
        activo = true;
        Serial.println("AUTENTICACION_CORRECTA");
        Serial.println("ms,ax,ay,az,gx,gy,gz");
      } else {
        Serial.println("CONTRASENA_INCORRECTA");
      }
    }
    delay(10); // Pequeña espera para no saturar
  }
}

void loop() {
  // Obtener el tiempo actual
  unsigned long currentMillis = millis();

  // Ejecutar si han pasado 10ms
  if (currentMillis - previousMillis >= interval) {
    // Guardamos el tiempo para el siguiente ciclo
    previousMillis = currentMillis;
    //definir variables de aceleración y giro
    int gx, gy, gz, ax, ay, az;
    // Lectura del sensor
    BMI160.readGyro(gx, gy, gz);
    BMI160.readAccelerometer(ax, ay, az);
    //Envío de datos por Serial
    Serial.print(currentMillis); Serial.print(",");
    Serial.print(ax); Serial.print(",");
    Serial.print(ay); Serial.print(",");
    Serial.print(az); Serial.print(",");
    Serial.print(gx); Serial.print(",");
    Serial.print(gy); Serial.print(",");
    Serial.println(gz);
  }
}