# Analisis de Avances (Task 1-2)
> Documentación Tangible que resume los procedimientos y logros alcanzados en el desarrollo de las tareas 1 y 2

- [Task l](#task1)
- [Task 2](#task2)

---

## Task1

A partir del uso de [Scrapy](https://thepythonscrapyplaybook.com/freecodecamp-beginner-course/) se realizo una plantilla con propiedades Automatizadas,
esta plantilla Posee

- **SPIDERS** : Rastreadores puros, se encargan de redireccionar y realizar peticiones a las paginas seleccionadas, poseen su metodos propios para filtrar y recolectar información
- **PIPELINES** : Se encargan de una vez generada la peticion, Filtrar y organizar la información predestinada, trabaja como un limpiador de datos anterior a la recolección de *Spider*
- **Items** : Plantillas de los objetos a recolectar, Ofrece una forma de definir los datos, evitando asi estar desordenados
- **Settings** : Módo de juego, define las reglas y el proceso de request

  Predeterminadamente, Scrapy solo ofrece un arreglo de modulos y paquetes con estas opciones, además de comandos y su propio interprete con el fin de probar, aplicar y diseñar de forma mas eficiente
  cada uno de los procesos que se quiere hacer.

   Cómo primer paso, nos enfatizamos en recolectar unicamente las categorias que posee la página [Olimpica](https://www.olimpica.com/), esto se realizo con ayuda de una interfaz de programación de
  la misma pagina, debido a que  naturalmente posee código dinámico, complejizando la lectura cuando se desconoce de el paradigma

Inicialmente se busca que los resultados se impriman directamente en la pantalla, parte de la tarea 2 será implementar una documentación y metodo de archivado

---

## Task2 

Durante el desarrollo de la tarea 2, se formo la estrucura principal que tendrá el primer tipo: **Categorias**, se aplicaron los primeros filtros de entrada (PIPELINES) y Se propuso el uso de archivos .json para la entrega de datos,

Se Propueso que el spider sea capaz de rastrear hasta sus las categorias y subcategorias, tras ser limpiadas, estructurarlas en objetos, y luego archivarlas en formatos JSON

