import React, { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StyleSheet, Text, View, Image, TouchableOpacity, ScrollView, ActivityIndicator, Alert, TextInput, Modal } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

const API_URL = 'http://192.168.1.212:8000/analizar-foto/';

export default function App() {
  // Estados para controlar la aplicación
  const [imagen, setImagen] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [resultado, setResultado] = useState(null);

  //info user
  const [modalVisible, setModalVisible] = useState(false);
  const [nombre, setNombre] = useState('');
  const [ocupacion, setOcupacion] = useState('');
  const [destino, setDestino] = useState('');

  // cargar datos
  useEffect(() => {
    const cargarPerfil = async () => {
      const n = await AsyncStorage.getItem('nombre');
      const o = await AsyncStorage.getItem('ocupacion');
      if (!n || !o) {
        setModalVisible(true);
      } else {
        setNombre(n);
        setOcupacion(o);
      }
    };
    cargarPerfil();
  }, []);

  const guardarPerfil = async () => {
    await AsyncStorage.setItem('nombre', nombre);
    await AsyncStorage.setItem('ocupacion', ocupacion);
    setModalVisible(false);
  };

  // Función para abrir la cámara del celular
  const tomarFoto = async () => {
    // Solicitar permisos de cámara
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permiso requerido', 'Necesitamos acceso a la cámara para analizar el entorno.');
      return;
    }

    // Abrir la cámara
    let result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true, 
      aspect: [4, 3],
      quality: 0.8, 
    });

    if (!result.canceled) {
      setImagen(result.assets[0].uri);
      setResultado(null); 
    }
  };

  const enviarAlBackend = async () => {
    if (!imagen) {
      Alert.alert('Error', 'Primero debes tomar una foto.');
      return;
    }

    setCargando(true);


    const formData = new FormData();
    const uriParts = imagen.split('.');
    const fileType = uriParts[uriParts.length - 1];

    formData.append('file', {
      uri: imagen,
      name: `photo.${fileType}`,
      type: `image/${fileType}`,
    });
    formData.append('nombre', nombre);
    formData.append('ocupacion', ocupacion);
    formData.append('destino', destino);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.ok) {
        throw new Error('Error en la respuesta del servidor');
      }

      const data = await response.json();
      setResultado(data); 
    } catch (error) {
      console.error(error);
      Alert.alert('Error de Conexión', 'No se pudo conectar con el servidor de FastAPI. Verifica la IP y que el backend esté corriendo.');
    } finally {
      setCargando(false);
    }
  };

  return (
      <>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.titulo}>Agente de Utilidad</Text>
        <Text style={styles.subtitulo}>Asistente de Salida Inteligente</Text>

        <TouchableOpacity onPress={() => setModalVisible(true)}>
          <Text style={{color: 'blue'}}>Editar Perfil</Text>
        </TouchableOpacity>
        
        {/* Contenedor de la Imagen */}
        <View style={styles.imageContainer}>
          {imagen ? (
            <Image source={{ uri: imagen }} style={styles.previewImage} />
          ) : (
            <Text style={styles.placeholderText}>No se ha capturado ninguna foto</Text>
          )}
        </View>
        {/* Sección de destino */}
        <TextInput 
          style={styles.input} 
          placeholder="¿A dónde vas? (opcional)" 
          value={destino} 
          onChangeText={setDestino} 
        />
        {/* Botones de Acción */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.buttonCamara} onPress={tomarFoto}>
            <Text style={styles.buttonText}>Tomar Foto</Text>
          </TouchableOpacity>

          {imagen && (
            <TouchableOpacity 
              style={[styles.buttonAnalizar, cargando && styles.buttonDeshabilitado]} 
              onPress={enviarAlBackend}
              disabled={cargando}
            >
              <Text style={styles.buttonText}>Analizar con IA</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Animación de carga */}
        {cargando && <ActivityIndicator size="large" color="#0000ff" style={{ marginTop: 20 }} />}
        
        {/* Sección de Resultados del Servidor */}
        {resultado && (
          <View style={styles.cardResultado}>
            <Text style={styles.cardTitulo}>Resultados del Análisis:</Text>

            <Text style={styles.objetosDetectados}>
              <Text style={{ fontWeight: 'bold' }}>Objetos Clave:</Text> {resultado.objetos.join(', ') || 'Ninguno detectado'}
            </Text>

            <View style={styles.lineaDivisoria} />

            <Text style={styles.cardSubtitulo}>Instrucciones del Asistente:</Text>
            <Text style={styles.textoAgente}>{resultado.respuesta}</Text>
          </View>
        )}
        
      </ScrollView>
      <Modal visible={modalVisible} animationType="slide">
        <View style={styles.modalContainer}>
          <Text style={styles.titulo}>Bienvenido</Text>
          <TextInput style={styles.input} placeholder="Nombre" value={nombre} onChangeText={setNombre} />
          <TextInput style={styles.input} placeholder="Ocupación" value={ocupacion} onChangeText={setOcupacion} />
          <TouchableOpacity style={styles.buttonAnalizar} onPress={guardarPerfil}>
            <Text style={styles.buttonText}>Guardar Perfil</Text>
          </TouchableOpacity>
        </View>
      </Modal>
  </>
  );
}

// Estilos de la Interfaz
const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#f5f6fa',
    alignItems: 'center',
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  titulo: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2f3640',
  },
  subtitulo: {
    fontSize: 16,
    color: '#718093',
    marginBottom: 20,
  },
  imageContainer: {
    width: '100%',
    height: 300,
    backgroundColor: '#dcdde1',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#b2bec3',
    marginBottom: 20,
  },
  previewImage: {
    width: '100%',
    height: '100%',
  },
  placeholderText: {
    color: '#7f8c8d',
    fontSize: 16,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 20,
  },
  buttonCamara: {
    flex: 1,
    backgroundColor: '#353b48',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginRight: 10,
  },
  buttonAnalizar: {
    flex: 1,
    backgroundColor: '#44bd32',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginLeft: 10,
  },
  buttonDeshabilitado: {
    backgroundColor: '#95afc0',
  },
  buttonText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  cardResultado: {
    width: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
    marginTop: 10,
  },
  cardTitulo: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2f3640',
    marginBottom: 10,
  },
  objetosDetectados: {
    fontSize: 15,
    color: '#2f3640',
    marginBottom: 10,
  },
  lineaDivisoria: {
    height: 1,
    backgroundColor: '#dcdde1',
    verticalAlign: 'middle',
    marginVertical: 10,
  },
  cardSubtitulo: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2f3640',
    marginBottom: 5,
  },
  input: {
  width: '100%',
  backgroundColor: '#fff',
  padding: 15,
  borderRadius: 10,
  borderWidth: 1,
  borderColor: '#dcdde1',
  marginBottom: 10,
  },
  textoAgente: {
    fontSize: 15,
    color: '#333',
    lineHeight: 22,
    fontStyle: 'italic',
  },
});