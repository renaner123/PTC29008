# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sensorapp.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='sensorapp.proto',
  package='sensor',
  syntax='proto2',
  serialized_pb=_b('\n\x0fsensorapp.proto\x12\x06sensor\"8\n\x06Sensor\x12\x0c\n\x04nome\x18\x01 \x02(\t\x12\r\n\x05valor\x18\x02 \x02(\x05\x12\x11\n\ttimestamp\x18\x03 \x01(\x05\"+\n\x06\x43onfig\x12\x0f\n\x07periodo\x18\x01 \x02(\x05\x12\x10\n\x08sensores\x18\x02 \x03(\t\")\n\x05\x44\x61\x64os\x12 \n\x08\x61mostras\x18\x01 \x03(\x0b\x32\x0e.sensor.Sensor\"b\n\x08Mensagem\x12\r\n\x05placa\x18\x01 \x02(\t\x12 \n\x06\x63onfig\x18\x02 \x01(\x0b\x32\x0e.sensor.ConfigH\x00\x12\x1e\n\x05\x64\x61\x64os\x18\x03 \x01(\x0b\x32\r.sensor.DadosH\x00\x42\x05\n\x03msg')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_SENSOR = _descriptor.Descriptor(
  name='Sensor',
  full_name='sensor.Sensor',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='nome', full_name='sensor.Sensor.nome', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='valor', full_name='sensor.Sensor.valor', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='sensor.Sensor.timestamp', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=27,
  serialized_end=83,
)


_CONFIG = _descriptor.Descriptor(
  name='Config',
  full_name='sensor.Config',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='periodo', full_name='sensor.Config.periodo', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sensores', full_name='sensor.Config.sensores', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=85,
  serialized_end=128,
)


_DADOS = _descriptor.Descriptor(
  name='Dados',
  full_name='sensor.Dados',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='amostras', full_name='sensor.Dados.amostras', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=130,
  serialized_end=171,
)


_MENSAGEM = _descriptor.Descriptor(
  name='Mensagem',
  full_name='sensor.Mensagem',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='placa', full_name='sensor.Mensagem.placa', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='config', full_name='sensor.Mensagem.config', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dados', full_name='sensor.Mensagem.dados', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='msg', full_name='sensor.Mensagem.msg',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=173,
  serialized_end=271,
)

_DADOS.fields_by_name['amostras'].message_type = _SENSOR
_MENSAGEM.fields_by_name['config'].message_type = _CONFIG
_MENSAGEM.fields_by_name['dados'].message_type = _DADOS
_MENSAGEM.oneofs_by_name['msg'].fields.append(
  _MENSAGEM.fields_by_name['config'])
_MENSAGEM.fields_by_name['config'].containing_oneof = _MENSAGEM.oneofs_by_name['msg']
_MENSAGEM.oneofs_by_name['msg'].fields.append(
  _MENSAGEM.fields_by_name['dados'])
_MENSAGEM.fields_by_name['dados'].containing_oneof = _MENSAGEM.oneofs_by_name['msg']
DESCRIPTOR.message_types_by_name['Sensor'] = _SENSOR
DESCRIPTOR.message_types_by_name['Config'] = _CONFIG
DESCRIPTOR.message_types_by_name['Dados'] = _DADOS
DESCRIPTOR.message_types_by_name['Mensagem'] = _MENSAGEM

Sensor = _reflection.GeneratedProtocolMessageType('Sensor', (_message.Message,), dict(
  DESCRIPTOR = _SENSOR,
  __module__ = 'sensorapp_pb2'
  # @@protoc_insertion_point(class_scope:sensor.Sensor)
  ))
_sym_db.RegisterMessage(Sensor)

Config = _reflection.GeneratedProtocolMessageType('Config', (_message.Message,), dict(
  DESCRIPTOR = _CONFIG,
  __module__ = 'sensorapp_pb2'
  # @@protoc_insertion_point(class_scope:sensor.Config)
  ))
_sym_db.RegisterMessage(Config)

Dados = _reflection.GeneratedProtocolMessageType('Dados', (_message.Message,), dict(
  DESCRIPTOR = _DADOS,
  __module__ = 'sensorapp_pb2'
  # @@protoc_insertion_point(class_scope:sensor.Dados)
  ))
_sym_db.RegisterMessage(Dados)

Mensagem = _reflection.GeneratedProtocolMessageType('Mensagem', (_message.Message,), dict(
  DESCRIPTOR = _MENSAGEM,
  __module__ = 'sensorapp_pb2'
  # @@protoc_insertion_point(class_scope:sensor.Mensagem)
  ))
_sym_db.RegisterMessage(Mensagem)


# @@protoc_insertion_point(module_scope)