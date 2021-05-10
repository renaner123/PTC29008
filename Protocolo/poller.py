#!/usr/bin/python3
# -*- coding: utf-8 -*- 

import selectors
import time
import crc
import random

class Callback:
  '''Classe Callback:
        
        Define uma classe base para os callbacks
        a serem usados pelo Poller. Cada objeto Callback
        contém um fileobj e um valor para timeout.
        Se fileobj for None, então o callback define 
        somente um timer.
        Esta classe DEVE ser especializada para que
        possa executar as ações desejadas para o tratamento
        do evento detectado pelo Poller.'''

  def __init__(self, fileobj=None, timeout=0):
      '''Cria um objeto Callback. 
      fileobj: objeto tipo arquivo, podendo ser inclusive 
      um descritor de arquivo numérico.
      timeout: valor de timeout em segundos, podendo ter parte 
      decimal para expressar fração de segundo'''
      if timeout < 0: raise ValueError('timeout negativo')
      self.fd = fileobj
      self._timeout = timeout
      self.base_timeout = timeout
      self._enabled = True
      self._enabled_to = True
      self._reloaded = False


  
  def handle(self):
      '''Trata o evento associado a este callback. Tipicamente 
      deve-se ler o fileobj e processar os dados lidos. Classes
      derivadas devem sobrescrever este método.'''
      pass

  def handle_timeout(self):
      '''Trata um timeout associado a este callback. Classes
      derivadas devem sobrescrever este método.'''
      pass

  def update(self, dt):
      'Atualiza o tempo restante de timeout'
      if not self._reloaded: self._timeout = max(0, self._timeout - dt)
      else: self._reloaded = False

  def reload_timeout(self):
      'Recarrega o valor de timeout'
      self._timeout = self.base_timeout
      self._reloaded = True

  def disable_timeout(self):
      'Desativa o timeout'
      self._enabled_to = False

  def enable_timeout(self):
      'Reativa o timeout'
      self._enabled_to = True

  def enable(self):
      'Reativa o monitoramento do descritor neste callback'
      self._enabled = True

  def disable(self):
      'Desativa o monitoramento do descritor neste callback'
      self._enabled = False
  def backoff(self):
      ''' Modifica o base_timeout para um valor de 1 a 7.
      '''
      self.disable_timeout()   
      self.base_timeout = random.randint(1, 7)
      self.reload_timeout()
      self.enable_timeout()

  def check_interval_Time(self):
    ''' Utilizado para cada 10 segundos fazer um ckeck de conexão. Utilizado no session_manage.py   
    '''
    self.disable_timeout()   
    self.base_timeout = random.randint(10,10)
    self.reload_timeout()
    self.enable_timeout()



  @property
  def timeout(self):
    return self._timeout

  @timeout.setter
  def timeout(self, tout):
    self._timeout = tout
    self._reloaded = True

  @property
  def timeout_enabled(self):
      return self._enabled_to
  
  @property
  def isTimer(self):
      'true se este callback for um timer'
      return self.fd == None

  @property
  def isEnabled(self):
      'true se monitoramento do descritor estiver ativado neste callback'
      return self._enabled
  
class Poller:
  '''Classe Poller: um agendador de eventos que monitora objetos
  do tipo arquivo e executa callbacks quando tiverem dados para 
  serem lidos. Callbacks devem ser registrados para que 
  seus fileobj sejam monitorados. Callbacks que não possuem
  fileobj são tratados como timers'''
  
  def __init__(self):
    self.cbs_to = []
    self.cbs = set()

  def adiciona(self, cb):
    'Registra um callback'
    if cb.isTimer and not cb in self.cbs_to: self.cbs_to.append(cb)
    else: self.cbs.add(cb)

  def _compareTimeout(self, cb, cb_to):
    if not cb.timeout_enabled: return cb_to
    if not cb_to:
        cb_to = cb
    elif cb_to.timeout > cb.timeout:
      cb_to = cb
    return cb_to







  def _timeout(self):
    cb_to = None
    for cb in self.cbs_to: cb_to = self._compareTimeout(cb, cb_to)
    for cb in self.cbs:
      cb_to = self._compareTimeout(cb, cb_to)
    return cb_to

  def despache(self):
    '''Espera por eventos indefinidamente, tratando-os com seus
    callbacks'''
    while True: self.despache_simples()

  def _get_events(self, timeout):
    sched = selectors.DefaultSelector()
    for cb in self.cbs:
      if cb.isEnabled: sched.register(cb.fd, selectors.EVENT_READ, cb)
    eventos = sched.select(timeout)
    return eventos

  def despache_simples(self):
    'Espera por um único evento, tratando-o com seu callback'
    t1 = time.time()
    cb_to = self._timeout()
    if cb_to != None:
        tout = cb_to.timeout
    else:
        tout = None
    eventos = self._get_events(tout)
    fired = set()
    if not eventos: # timeout !
      if cb_to != None:
          fired.add(cb_to)
          cb_to.handle_timeout()
          cb_to.reload_timeout()
    else:
      for key,mask in eventos:
        cb = key.data # este é o callback !
        fired.add(cb)
        cb.handle()
        cb.reload_timeout()
    dt = time.time() - t1
    for cb in self.cbs_to:
      if not cb in fired: cb.update(dt)
    for cb in self.cbs:
      if not cb in fired: cb.update(dt)


class Layer(Callback):
      def __init__(self, top=None, bottom=None):
        self.top = top
        self.bottom = bottom       

      def handle(self):
        pass
          
      def handle_timeout(self):
        pass

      def sendToLayer(self, date):
        pass

      def notifyLayer(self, date):
        pass 
      
      def get_framming(self,dade):
        pass
      
