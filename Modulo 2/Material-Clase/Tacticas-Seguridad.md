# Tácticas de Seguridad — deck oficial del Módulo 2

> **Tipo:** `material-oficial` (Recursos complementarios, Brightspace, Unidad 3 de 5).
> **Fuente:** `TacticasSeguridad.pptx` — Bass, Clements, Kazman, *Software Architecture in Practice*, 4th ed. (citado en el propio deck).
> **Extraído:** 2026-09-30, texto de las láminas tal cual. Se tradujo del inglés con traducción automática en el deck original (hay frases torpes).
> **Límite de la extracción:** solo texto. Los diagramas, figuras y tablas dibujadas como imagen NO están; las láminas que quedan vacías o con solo título dependen de una imagen.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

SEGURIDAD

(SECURITY)

## Lámina 2

Seguridad - Security

La Seguridad es una medida de la capacidad del sistema para proteger los datos y la información del acceso no autorizado y al mismo tiempo proporcionar acceso a las personas y los sistemas que están autorizados. Un ataque, es decir, una acción realizada contra un sistema informático con la intención de causar daño, puede tomar varias formas. Puede tratarse de un intento no autorizado de acceder a datos o servicios o de modificar datos, o puede tener la intención de denegar servicios a usuarios legítimos.

Definición

## Lámina 3

Seguridad - Security

El enfoque más simple para caracterizar la seguridad se centra en tres características: Confidencialidad, Integridad y Disponibilidad:

La confidencialidad es la propiedad de que los datos o servicios están protegidos contra el acceso no autorizado. Por ejemplo, un pirata informático no puede acceder a sus declaraciones de impuestos sobre la renta en una computadora del gobierno.

La integridad es la propiedad de que los datos o servicios no están sujetos a manipulación no autorizada. Por ejemplo, su calificación no ha cambiado desde que su instructor la asignó.

La disponibilidad es la propiedad de que el sistema estará disponible para un uso legítimo. Por ejemplo, un ataque de denegación de servicio no le impedirá pedir este libro en una librería en línea.

Definición

## Lámina 4

Seguridad - Security

Un tema muy relacionado con la seguridad es la calidad de la privacidad. Las preocupaciones sobre la privacidad se han vuelto más importantes en los últimos años y están consagradas en la ley en la Unión Europea a través del Reglamento General de Protección de Datos (GDPR). Otras jurisdicciones han adoptado regulaciones similares.

Lograr la privacidad se trata de limitar el acceso a la información, lo que a su vez se trata de qué información se debe limitar el acceso y a quién se debe permitir el acceso. El término general para la información que debe mantenerse privada es información de identificación personal (PII).

Privacidad

## Lámina 5

Seguridad - Security

El Instituto Nacional de Estándares y Tecnología (NIST) define la PII como “cualquier información sobre una persona mantenida por una agencia, incluida (1) cualquier información que pueda usarse para distinguir o rastrear la identidad de una persona, como nombre, número de seguro social, fecha y lugar de nacimiento, apellido de soltera de la madre o registros biométricos; y (2) cualquier otra información que esté vinculada o pueda vincularse a un individuo, como información médica, educativa, financiera y laboral”.

Privacidad

## Lámina 6

ESCENARIO

## Lámina 7

Seguridad - Security

Escenario General

Portion of Scenario

Description

Possible Values

Source

The attack may be from outside the organization or from inside the organization. The source of the attack may be either a human or another system. It may have been previously identified (either correctly or incorrectly) or may be currently unknown.

Human

Another system

which is:

Inside the organization

Outside the organization

Previously identified

Unknown

Stimulus

The stimulus is an attack.

An unauthorized attempt to:

Display data

Capture data

Change or delete data

Access system services

Change the system’s behavior

Reduce availability

## Lámina 8

Seguridad - Security

Escenario General

Portion of Scenario

Description

Possible Values

Artifacts

What is the target of the attack?

System services

Data within the system

A component or resources of the system

Data produced or consumed by the system

Environment

What is the state of the system when the attack occurs?

The system is:

Online or offline

Connected to or disconnected from a network

Behind a firewall or open to a network

Fully operational

Partially operational

Not operational

Response

The system ensures that confidentiality, integrity, and availability are maintained.

Transactions are carried out in a fashion such that

## Lámina 9

Seguridad - Security

Escenario General

Portion of Scenario

Description

Possible Values

Response

The system ensures that confidentiality, integrity, and availability are maintained.

Transactions are carried out in a fashion such that

Data or services are protected from unauthorized access

Data or services are not being manipulated without authorization

Parties to a transaction are identified with assurance

The parties to the transaction cannot repudiate their involvements

The data, resources, and system services will be available for legitimate use

## Lámina 10

Seguridad - Security

Escenario General

Portion of Scenario

Description

Possible Values

Response

The system ensures that confidentiality, integrity, and availability are maintained.

The system tracks activities within it by

Recording access or modification

Recording attempts to access data, resources, or services

Notifying appropriate entities (people or systems) when an apparent attack is occurring

## Lámina 11

Seguridad - Security

Escenario General

Portion of Scenario

Description

Possible Values

Response measure

Measures of a system’s response are related to the frequency of successful attacks, the time and cost to resist and repair attacks, and the consequential damage of those attacks.

One or more of the following:

How much of a resource is compromised or ensured

Accuracy of attack detection

How much time passed before an attack was detected

How many attacks were resisted

How long it takes to recover from a successful attack

How much data is vulnerable to a particular attack

## Lámina 12

Seguridad - Security

Ejemplo de un Escenario concreto

Un empleado descontento en una ubicación remota intenta modificar incorrectamente la tabla de tasas de pago durante las operaciones normales. Se detecta el acceso no autorizado, el sistema mantiene un registro de auditoría y los datos correctos se restauran en un día.

## Lámina 13

TÁCTICAS

## Lámina 14

Seguridad - Security

Tácticas

Un método para pensar en cómo lograr la Seguridad en un sistema es centrarse en la seguridad física. Las instalaciones seguras solo permiten un acceso limitado a ellas (p. ej., mediante el uso de vallas y puntos de control de seguridad), tienen medios para detectar intrusos (p. ej., exigiendo que los visitantes legítimos lleven insignias), tienen mecanismos de disuasión (p. ej., con guardias armados), tienen capacidad de reacción (p. ej., cierre automático de puertas) y mecanismos de recuperación (p. ej., copia de seguridad fuera del sitio). Estos conducen a nuestras cuatro categorías de tácticas: detectar, resistir, reaccionar y recuperarse.

## Lámina 15

Seguridad - Security

Tácticas

Fuente: Software Architecture in Practice, 4th Edition

## Lámina 16

Seguridad - Security

Tácticas - Detectar Ataques

Detectar intrusión. Esta táctica compara el tráfico de red o los patrones de solicitud de servicios dentro de un sistema con un conjunto de firmas o patrones conocidos de comportamiento malicioso almacenados en una base de datos. Las firmas se pueden basar en las características del protocolo, las características de la solicitud, los tamaños de la carga útil, las aplicaciones, la dirección de origen o destino o el número de puerto.

## Lámina 17

Seguridad - Security

Tácticas - Detectar Ataques

Detectar denegación de servicio. Esta táctica compara el patrón o la firma del tráfico de red que ingresa a un sistema con perfiles históricos de ataques de denegación de servicio (DoS) conocidos.

## Lámina 18

Seguridad - Security

Tácticas - Detectar Ataques

Verificar la integridad del mensaje. Esta táctica emplea técnicas como sumas de verificación o valores hash para verificar la integridad de los mensajes, archivos de recursos, archivos de implementación y archivos de configuración. Una suma de verificación es un mecanismo de validación en el que el sistema mantiene por separado información redundante para archivos y mensajes, y utiliza esta información redundante para verificar el archivo o mensaje. Un valor hash es una cadena única generada por una función hash, cuya entrada puede ser archivos o mensajes. Incluso un ligero cambio en los archivos o mensajes originales da como resultado un cambio significativo en el valor hash.

## Lámina 19

Seguridad - Security

Tácticas - Detectar Ataques

Detectar anomalías en la entrega de mensajes. Esta táctica busca detectar posibles ataques de intermediarios, en los que una parte malintencionada intercepta (y posiblemente modifica) los mensajes. Si los tiempos de entrega de mensajes son normalmente estables, al verificar el tiempo que lleva entregar o recibir un mensaje, es posible detectar un comportamiento de tiempo sospechoso. Del mismo modo, un número anormal de conexiones y desconexiones puede indicar un ataque de este tipo.

## Lámina 20

Seguridad - Security

Tácticas - Resistir Ataques

Identificar actores. La identificación de actores (usuarios o computadoras remotas) se enfoca en identificar la fuente de cualquier entrada externa al sistema. Los usuarios generalmente se identifican a través de ID de usuario. Otros sistemas pueden ser "identificados" a través de códigos de acceso, direcciones IP, protocolos, puertos o algún otro medio.

## Lámina 21

Seguridad - Security

Tácticas - Resistir Ataques

Autenticar actores. La autenticación significa garantizar que un actor es realmente quien o lo que pretende ser. Las contraseñas, las contraseñas de un solo uso, los certificados digitales, la autenticación de dos factores y la identificación biométrica proporcionan un medio para la autenticación. Otro ejemplo es CAPTCHA (Prueba de Turing pública completamente automatizada para diferenciar a las computadoras de los humanos), un tipo de prueba de desafío-respuesta que se utiliza para determinar si el usuario es humano. Los sistemas pueden requerir una reautenticación periódica, como cuando su teléfono inteligente se bloquea automáticamente después de un período de inactividad.

## Lámina 22

Seguridad - Security

Tácticas - Resistir Ataques

Autorizar actores. Autorización significa garantizar que un actor autenticado tiene los derechos para acceder y modificar datos o servicios. Este mecanismo generalmente se habilita al proporcionar algunos mecanismos de control de acceso dentro de un sistema. El control de acceso se puede asignar por actor, por clase de actor o por función.

## Lámina 23

Seguridad - Security

Tácticas - Resistir Ataques

Acceso limitado. Esta táctica consiste en limitar el acceso a los recursos informáticos. Limitar el acceso puede significar restringir la cantidad de puntos de acceso a los recursos o restringir el tipo de tráfico que puede pasar a través de los puntos de acceso. Ambos tipos de límites minimizan la superficie de ataque de un sistema. Por ejemplo, una zona desmilitarizada (DMZ) se usa cuando una organización quiere permitir que los usuarios externos accedan a ciertos servicios pero no a otros. La DMZ se encuentra entre Internet y una intranet, y está protegida por un par de firewalls, uno a cada lado. El cortafuegos interno es un único punto de acceso a la intranet; funciona como un límite para el número de puntos de acceso y controla el tipo de tráfico permitido a través de la intranet.

## Lámina 24

Seguridad - Security

Tácticas - Resistir Ataques

Limite la exposición. Esta táctica se enfoca en minimizar los efectos del daño causado por una acción hostil. Es una defensa pasiva ya que no evita de forma proactiva que los atacantes hagan daño. La limitación de la exposición generalmente se realiza al reducir la cantidad de datos o servicios a los que se puede acceder a través de un único punto de acceso y, por lo tanto, se ven comprometidos en un solo ataque.

## Lámina 25

Seguridad - Security

Tácticas - Resistir Ataques

Cifrar datos. La confidencialidad generalmente se logra aplicando alguna forma de encriptación a los datos y la comunicación. El cifrado brinda protección adicional a los datos mantenidos de manera persistente más allá de la que está disponible a partir de la autorización. Los enlaces de comunicación, en comparación, pueden no tener controles de autorización. En tales casos, el cifrado es la única protección para pasar datos a través de enlaces de comunicación de acceso público. El cifrado puede ser simétrico (los lectores y escritores usan la misma clave) o asimétrico (los lectores y escritores usan claves públicas y privadas emparejadas).

## Lámina 26

Seguridad - Security

Tácticas - Resistir Ataques

Entidades separadas. La separación de diferentes entidades limita el alcance de un ataque. La separación dentro del sistema se puede realizar a través de la separación física en diferentes servidores conectados a diferentes redes, el uso de máquinas virtuales o un "espacio de aire", es decir, al no tener una conexión electrónica entre las diferentes partes de un sistema. Finalmente, los datos confidenciales se separan con frecuencia de los datos no confidenciales para reducir la posibilidad de ataques por parte de los usuarios que tienen acceso a datos no confidenciales.

## Lámina 27

Seguridad - Security

Tácticas - Resistir Ataques

Validar entrada. Limpiar y verificar la entrada a medida que la recibe un sistema, o parte de un sistema, es una importante línea de defensa inicial para resistir los ataques. Esto a menudo se implementa mediante el uso de un marco de seguridad o una clase de validación para realizar acciones como el filtrado, la canonicalización y la desinfección de la entrada. La validación de datos es la principal forma de defensa contra ataques como la inyección SQL, en la que se inserta código malicioso en sentencias SQL, y el cross-site scripting (XSS), en el que el código malicioso de un servidor se ejecuta en un cliente.

## Lámina 28

Seguridad - Security

Tácticas - Resistir Ataques

Cambiar la configuración de credenciales. Muchos sistemas tienen configuraciones de seguridad predeterminadas asignadas cuando se entrega el sistema. Obligar al usuario a cambiar esa configuración evitará que los atacantes obtengan acceso al sistema a través de configuraciones que pueden estar disponibles públicamente. De manera similar, muchos sistemas requieren que los usuarios elijan una nueva contraseña después de un período de tiempo máximo.

## Lámina 29

Seguridad - Security

Tácticas - Reaccionar a Ataques

Revocar el acceso. Si el sistema o un administrador del sistema cree que se está produciendo un ataque, el acceso puede verse severamente limitado a recursos confidenciales, incluso para usuarios y usos normalmente legítimos. Por ejemplo, si su escritorio se vio comprometido por un virus, su acceso a ciertos recursos puede estar limitado hasta que elimine el virus de su sistema.

## Lámina 30

Seguridad - Security

Tácticas - Reaccionar a Ataques

Restringir inicio de sesión. Los intentos fallidos repetitivos de inicio de sesión pueden indicar un posible ataque. Muchos sistemas limitan el acceso desde una computadora en particular si hay repetidos intentos fallidos de acceder a una cuenta desde esa computadora. Por supuesto, los usuarios legítimos pueden cometer errores al intentar iniciar sesión, por lo que el acceso limitado puede durar solo un cierto período de tiempo. En algunos casos, los sistemas duplican el período de tiempo de bloqueo después de cada intento fallido de inicio de sesión.

## Lámina 31

Seguridad - Security

Tácticas - Reaccionar a Ataques

Informar a los actores. Los ataques en curso pueden requerir la acción de los operadores, otro personal o sistemas cooperantes. Dicho personal o sistemas, el conjunto de actores relevantes, deben ser notificados cuando el sistema ha detectado un ataque.

## Lámina 32

Seguridad - Security

Tácticas - Recuperarse de Ataques

Auditoría. Auditamos los sistemas, es decir, mantenemos un registro de las acciones del usuario y del sistema y sus efectos, para ayudar a rastrear las acciones de un atacante e identificarlo. Podemos analizar las pistas de auditoría para intentar enjuiciar a los atacantes o crear mejores defensas en el futuro.

## Lámina 33

Seguridad - Security

Tácticas - Recuperarse de Ataques

No repudio. Esta táctica garantiza que el remitente de un mensaje no pueda negar posteriormente haber enviado el mensaje y que el destinatario no pueda negar haber recibido el mensaje. Por ejemplo, no puede negarse a pedir algo por Internet, y el comerciante no puede negarse a recibir su pedido. Esto podría lograrse con alguna combinación de firmas digitales y autenticación por parte de terceros confiables.

## Lámina 34

PATRONES

## Lámina 35

Seguridad - Security

Patrones - Intercepting Validator

Validador interceptor. Este patrón inserta un elemento de software, un envoltorio, entre el origen y el destino de los mensajes. Este enfoque adquiere mayor importancia cuando la fuente de los mensajes está fuera del sistema. La responsabilidad más común de este patrón es implementar la táctica de verificación de la integridad del mensaje, pero también puede incorporar tácticas como detectar intrusiones y detectar denegación de servicio (al comparar mensajes con patrones de intrusión conocidos) o detectar anomalías en la entrega de mensajes.

## Lámina 36

Seguridad - Security

Patrones – Intercepting Validator

Beneficios

Según el validador específico que cree e implemente, este patrón puede cubrir la mayor parte de la línea de costa de la categoría de tácticas de "detección de ataques", todo en un solo paquete.

## Lámina 37

Seguridad - Security

Patrones – Intercepting Validator

Tradeoffs

Como siempre, la introducción de un intermediario exige un precio de rendimiento. Los patrones de intrusión cambian y evolucionan con el tiempo, por lo que este componente debe mantenerse actualizado para que mantenga su eficacia. Esto impone una obligación de mantenimiento a la organización responsable del sistema.

## Lámina 38

Seguridad - Security

Patrones - Intrusion Prevention System (IPS)

Sistema de Prevención de Intrusión. Un sistema de prevención de intrusiones (IPS) es un elemento independiente cuyo objetivo principal es identificar y analizar cualquier actividad sospechosa. Si la actividad se considera aceptable, se permite. Por el contrario, si es sospechosa, la actividad se previene y denuncia. Estos sistemas buscan patrones sospechosos de uso general, no solo mensajes anómalos.

## Lámina 39

Seguridad - Security

Patrones - Intrusion Prevention System (IPS)

Beneficios

Estos sistemas pueden abarcar la mayoría de las tácticas de "detectar ataques" y "reaccionar a los ataques".

## Lámina 40

Seguridad - Security

Patrones - Intrusion Prevention System (IPS)

Tradeoffs

Los patrones de actividad que busca un IPS cambian y evolucionan con el tiempo, por lo que la base de datos de patrones debe estar constantemente actualizada.

Los sistemas que emplean un IPS incurren en un costo de rendimiento.

Los IPS están disponibles como componentes comerciales listos para usar, lo que hace que no sea necesario desarrollarlos, pero quizás no se adapten del todo a una aplicación específica.

## Lámina 41

Seguridad - Security

Lecturas Recomendadas

OWASP Top Ten 2021

CWE/SANS TOP 25 Most Dangerous Software Errors

Fundamental Practices for Secure Software Development, Third Edition

Awesome Penetration Testing

SAST vs DAST What they are and when to use them

## Lámina 42

Bibliografía

Len Bass, Paul Clements, Rick Kazman. Software Architecture in Practice. 4th Edition. SEI / Addison-Wesley, 2022​

## Lámina 43

_(sin texto: la lámina es una imagen)_
