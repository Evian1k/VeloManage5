import api from './api';

class AppointmentService {
  async getAppointments(status = null, startDate = null, endDate = null) {
    try {
      const params = {};
      if (status) params.status = status;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await api.get('/appointments', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get appointments');
    }
  }

  async getAppointment(id) {
    try {
      const response = await api.get(`/appointments/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get appointment');
    }
  }

  async createAppointment(appointmentData) {
    try {
      const response = await api.post('/appointments', appointmentData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create appointment');
    }
  }

  async updateAppointment(id, appointmentData) {
    try {
      const response = await api.put(`/appointments/${id}`, appointmentData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update appointment');
    }
  }

  async deleteAppointment(id) {
    try {
      const response = await api.delete(`/appointments/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to delete appointment');
    }
  }

  async confirmAppointment(id, mechanicId = null) {
    try {
      const data = mechanicId ? { mechanic_id: mechanicId } : {};
      const response = await api.put(`/appointments/${id}/confirm`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to confirm appointment');
    }
  }

  async startAppointment(id) {
    try {
      const response = await api.put(`/appointments/${id}/start`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to start appointment');
    }
  }

  async completeAppointment(id) {
    try {
      const response = await api.put(`/appointments/${id}/complete`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to complete appointment');
    }
  }

  async cancelAppointment(id) {
    try {
      const response = await api.put(`/appointments/${id}/cancel`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to cancel appointment');
    }
  }

  async getAvailableSlots(date, serviceId = null) {
    try {
      const params = { date };
      if (serviceId) params.service_id = serviceId;
      
      const response = await api.get('/appointments/available-slots', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get available slots');
    }
  }

  async getUpcomingAppointments() {
    try {
      const response = await api.get('/appointments/upcoming');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get upcoming appointments');
    }
  }
}

export const appointmentService = new AppointmentService();