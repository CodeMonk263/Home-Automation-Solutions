import React, { Component } from 'react';
import Card from 'react-bootstrap/Card';
import '@aws-amplify/ui/dist/style.css';

import ToggleSwitch from './ToggleSwitch';

class Sensors extends Component {

  render() {
    const data = this.props.get_state(this.props.name);
    return(
        <div className="Sensor">
            <Card style={{ width: '18rem' }}>
                <Card.Body>
                    <Card.Title>{this.props.name}</Card.Title>
                    <Card.Text> 
                        { data } - { this.props.unit }
                    </Card.Text>
                    {this.props.name === "Lights" ?
                      <ToggleSwitch className="d-flex" checked={this.props.notif_state} onchange={(value) => this.props.toggle(value)} />
                    : null}
                </Card.Body>
            </Card>
            <style jsx>{
            `
            .Sensor {
                    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                    transition: 0.3s;
                }
                
                .Sensor:hover {
                    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
                }
                `
            }
            </style>
        </div>
    )
  }
}

export default Sensors;
