import api from './api';

class VehicleService {
  async getVehicles() {
    try {
      const response = await api.get('/vehicles');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get vehicles');
    }
  }

  async getVehicle(id) {
    try {
      const response = await api.get(`/vehicles/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get vehicle');
    }
  }

  async createVehicle(vehicleData) {
    try {
      const response = await api.post('/vehicles', vehicleData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create vehicle');
    }
  }

  async updateVehicle(id, vehicleData) {
    try {
      const response = await api.put(`/vehicles/${id}`, vehicleData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update vehicle');
    }
  }

  async deleteVehicle(id) {
    try {
      const response = await api.delete(`/vehicles/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to delete vehicle');
    }
  }

  async getVehicleServiceHistory(id) {
    try {
      const response = await api.get(`/vehicles/${id}/service-history`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get service history');
    }
  }

  async getServiceReminder(id) {
    try {
      const response = await api.get(`/vehicles/${id}/service-reminder`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get service reminder');
    }
  }

  async searchVehicles(params) {
    try {
      const response = await api.get('/vehicles/search', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to search vehicles');
    }
  }
}

export const vehicleService = new VehicleService();