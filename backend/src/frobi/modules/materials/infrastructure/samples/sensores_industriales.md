# Guía de sensores industriales

## Qué es un sensor
Un sensor es un dispositivo que mide una magnitud física, como la temperatura, la presión, la distancia o la presencia de un objeto, y la convierte en una señal eléctrica que un controlador puede leer. En una planta industrial los sensores son los "sentidos" de la máquina: sin ellos, el controlador no sabe qué está pasando.

## Señales analógicas y digitales
Un sensor digital entrega solo dos estados, por ejemplo "hay pieza" o "no hay pieza". Un sensor analógico entrega un valor continuo, normalmente de 4 a 20 mA o de 0 a 10 V, que representa cuánto mide. La señal de 4 a 20 mA es muy usada porque resiste el ruido eléctrico y permite detectar un cable cortado: si la corriente baja de 4 mA, algo falla.

## Sensores inductivos
Los sensores inductivos detectan metales sin contacto. Generan un campo magnético y notan el cambio cuando una pieza metálica se acerca. Su distancia de detección es corta, de unos pocos milímetros. Se usan para contar piezas metálicas, detectar la posición de un cilindro o confirmar que una tapa metálica está puesta.

## Sensores capacitivos
Los sensores capacitivos detectan metales y también materiales no metálicos, como plásticos, madera, granos y líquidos. Funcionan midiendo el cambio de capacidad eléctrica cuando un objeto entra en su zona. Por eso se usan para medir el nivel de un líquido a través de la pared de un tanque de plástico o para detectar botellas en una línea de envasado.

## Sensores fotoeléctricos
Los sensores fotoeléctricos usan un haz de luz. Detectan un objeto cuando este interrumpe o refleja la luz. Alcanzan distancias mayores que los inductivos y capacitivos, a veces de varios metros, pero el polvo o el vapor pueden afectarlos.

## Sensores de temperatura
El termopar mide temperatura gracias a la unión de dos metales distintos, que produce un pequeño voltaje que cambia con el calor. Soporta temperaturas muy altas, por ejemplo en hornos. La RTD, como la Pt100, mide temperatura por el cambio de resistencia de un metal; es más precisa que el termopar, pero trabaja en rangos más bajos.

## Sensores de presión
Un transmisor de presión convierte la presión de un fluido en una señal eléctrica, casi siempre de 4 a 20 mA. Se usa para vigilar compresores, tuberías y sistemas hidráulicos.

## Cómo elegir un sensor
Para elegir un sensor hay que preguntarse: qué se quiere detectar o medir, de qué material es el objeto, a qué distancia está, en qué ambiente trabaja (polvo, humedad, temperatura) y qué tipo de señal acepta el controlador.
