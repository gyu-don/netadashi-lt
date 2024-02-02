import React, { useState, ChangeEvent, FormEvent } from 'react';
import Form from 'react-bootstrap/Form';

export interface ReservationData {
  name: string;
  start: number;
  end: number;
}

export interface ReservationProps {
    defaultFormData: ReservationData;
    handleUpdateFormData: (reservation: ReservationData) => void;
  }
  
export const Reservation: React.FC<ReservationProps> = ({ defaultFormData, handleUpdateFormData }) => {
  const [formData, setFormData] = useState<ReservationData>(defaultFormData);

  const handleChange = (event: ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: name === 'name' ? value : parseInt(value, 10)
    });
    handleUpdateFormData({
      ...formData,
      [name]: name === 'name' ? value : parseInt(value, 10)
    });
    
  };

  return (
    <Form.Group className="mb-3">
      <Form.Label>
        名前:
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
        />
      </Form.Label>
      <Form.Label>
        開始時間:
        <input
          type="number"
          name="start"
          value={formData.start}
          onChange={handleChange}
        />
      </Form.Label>
      <Form.Label>
        終了時間:
        <input
          type="number"
          name="end"
          value={formData.end}
          onChange={handleChange}
        />
      </Form.Label>
    </Form.Group>
  );
}