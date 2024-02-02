import React from 'react';
import './App.css';

import ThemeProvider from 'react-bootstrap/ThemeProvider';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert'
import Table from 'react-bootstrap/Table'
import 'bootstrap/dist/css/bootstrap.min.css';

import {Reservation, ReservationData} from "./Reservation"

interface ResponseData {
  result: ReservationData[][];
  check_constr: boolean;
  energy: number;
}

const max_time: number = 15;

export default class App extends React.Component<{}, { responseData: ResponseData | null, reservationData: ReservationData[] }> {
  constructor(props: {}) {
    super(props);
    const reservationData: ReservationData[] = Array.from({ length: 10 }, (_, index) => {
      const start = Math.floor(Math.random() * 10) + 1;
      const end = start + Math.floor(Math.random() * 3) + 1;
      return {
        name: `予約${index + 1}`,
        start,
        end
      }
    });
    this.state = {
      responseData: null,
      reservationData,
    };
  }

  async handleCalcClick(reservations: ReservationData[]): Promise<void> {
    try {
      console.log(reservations)
      const response = await fetch('http://127.0.0.1:5000/solve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reservations)
      });

      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }

      const data: ResponseData = await response.json();
      console.log(data);
      this.setState({ responseData: data });
    } catch (error) {
      console.error('Error:', error);
    }
  };


  render() {
    const { responseData } = this.state;
    const reservations = Array.from({ length: 10 }, (_, index) => {
      return (
        <Reservation key={index} defaultFormData={this.state.reservationData[index]} handleUpdateFormData={(reservation: ReservationData) => {
          const {responseData, reservationData} = this.state;
          reservationData[index] = reservation;
          this.setState({responseData, reservationData});
        }} />
      );
    });

    return (
      <div>
      <Form>
        {reservations}
        <Button variant="primary" onClick={() => this.handleCalcClick(reservations.map((reservation) => {return reservation.props.defaultFormData}))}>計算</Button>
      </Form>
      {responseData && (
        <div>
          {responseData.check_constr === false && <Alert key="danger">予約が成立しませんでした(制約違反)</Alert>}
          {responseData.energy > 0.0 && <Alert key="warning">予約が成立しませんでした</Alert>}
          <Table>
            <thead>
              <tr>
                <th>会議室</th>
                {[...Array(max_time).keys()].map(index => <th key={index + 1}>{index + 1}</th>)}
              </tr>
            </thead>
            <tbody>
              {responseData.result.map((roomReservations, roomIndex) => (
                <tr key={roomIndex}>
                  <td>{`会議室${roomIndex + 1}`}</td>
                  {(() => {
                    let schedule = [...Array(max_time).keys()].map(index => "");
                    for (const reservation of roomReservations) {
                      for (let t = reservation.start; t < reservation.end; t++) {
                        schedule[t - 1] += reservation.name;
                      }
                    }
                    return schedule;
                  })().map((name, index) => (
                    <td key={index} style={{"width": "80px"}}>
                      {name}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
      </div>
    );
  }
  
}