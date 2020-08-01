import React, { Component } from 'react';
import './App.css';

import 'bootstrap/dist/css/bootstrap.min.css';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import Sensors from "./components/sensorData"

import Amplify from 'aws-amplify';
import awsconfig from './aws-exports';
import { withAuthenticator } from 'aws-amplify-react';
import '@aws-amplify/ui/dist/style.css';

import axios from "axios";

Amplify.configure(awsconfig);

class App extends Component{
  constructor(props) {
    super(props);
    this.state = {
      Lights: "OFF",
      Surveillance: "None",
      notif_state: false,
      Light_Reading: "BRIGHT"
    };
    this.get_state = this.get_state.bind(this);
    this.request_get = this.request_get.bind(this);
    this.toggle = this.toggle.bind(this);
  }

  toggle(value) {
    this.setState({notif_state: value});
    axios.post('http://192.168.0.109:8000/api/method_update/', 
    {
      "ultrasonic_state": value ? "ON" : "OFF",
      "light_reading": this.state.Light_Reading === "BRIGHT" ? "ON" : "OFF",
      "face_data": this.state.Surveillance
    },
    {
      headers: {
          'Content-Type': 'application/json'
      }
    })
    .then(res => {
      console.log(res.data);
    })
    .catch(err => console.log(err))
  }

  componentDidMount() {
    this.interval = setInterval(() => this.request_get(), 3000)
  }
  
  request_get() {
    axios.get("http://192.168.0.109:8000/api/method_update")
    .then(res => {
      const status = res.data.ultrasonic_state;
      const cam_data = res.data.face_data;
      const light = res.data.light_reading;
      this.setState({ Lights: status, 
                      Surveillance: cam_data, 
                      Light_Reading: light === "ON" ? "BRIGHT" : "DARK", 
                      notif_state: status === "ON" ? true : false });
    })
  }

  get_state(name) {
    return this.state[name]
  }

  render() {
    return (
      <div className="App">
        <Container className="p-4">
          <Row className="p-3 justify-content-md-center">
            <Col md="auto"> <Sensors name="Lights" unit="Status" notif_state={this.state.notif_state} toggle={this.toggle} get_state={this.get_state}/> </Col>
            <Col md="auto"> <Sensors name="Surveillance" unit="Intruder" get_state={this.get_state}/> </Col>
            <Col md="auto"> <Sensors name="Light_Reading" unit = "Room" get_state={this.get_state}/> </Col>
          </Row>
          <Row className="p-3 justify-content-md-center">
            <Col md="auto">  Type this command in your cmd to obtain image of intruder -> scp pi@192.168.0.109:/home/pi/Documents/sensor-nodes/src/images/face* . </Col>
          </Row>
        </Container>
      </div>
    );
  }
}

export default withAuthenticator(App, true);
