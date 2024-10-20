# Основы компьютерных сетей    
------------------------------------------------------------------       
## Содержание    

1. [Используемые средства разработки](#prog)    
2. [Лабораторная работа №1](#first)    
   2.1. [Условие. Ссылка на файл условия](#first_task)   
   2.2. [Как запустить](#first_run)

------------------------------------------------------------------    
<a name = "prog" />    

## Используемые средства разработки    

__ОС__: Linux Fedora 40    
__Язык программирования__: Python    

------------------------------------------------------------------   
<a name = "first" />

## Лабораторная работа №1    

<a name = "first_task" />    

### Условие    

Написать коммуникационную программу, которая была бы совместима со следующей топологией:    
![Топология: x->x+1 для чтения и записи](img/topology.jpg)    

__Требования__:    
1. Программа должна передавать и принимать данные через разные
COM-порты.    
2. Программа должна быть собственно цельной программой
(отдельным приложением), работающей на передачу и на прием (количество
потоков и так далее не регламентировано).    
3. COM-порты должно выбирать вручную после запуска программы --
с возможностью последующей замены.    
4. Данные должны передаваться посимвольно, причем как «сырой
поток».

<a name = "first_run" />

### Как запустить    

Для начала следует открыть порты, например, с помощью утилиты socat:    
```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0 
```

Вывод программы будет примерно следующий:    
```bash    
2024/10/11 01:53:28 socat[3796] N PTY is /dev/pts/4
2024/10/11 01:53:28 socat[3796] N PTY is /dev/pts/5
2024/10/11 01:53:28 socat[3796] N starting data transfer loop with FDs [5,5] and [7,7]
```    

Порты открыты, теперь, чтобы ими пользоваться, достаточно создать симлинки с `/dev/pts/5` и `/dev/pts/6`  с необходимыми номерами портов на `/dev/ttySx`, где x — номер необходимого порта.     
Например, так:    
```bash
sudo ln -s /dev/pts/4 /dev/ttyS1
sudo ln -s /dev/pts/5 /dev/ttyS2
```    
Это следует повторить и для второй пары портов

Теперь склонируйте себе репозиторий.     
Собрать проект в исполняемый файл можно с помощью утилиты `pyinstaller`:    
```bash
pyinstaller --onefile --hidden-import=serial --windowed main.py
```

Всё, достаточно теперь запустить две копии приложения и пользоваться!


   
