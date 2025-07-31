import api from './api';

class ServiceService {
  // Services
  async getServices(category = null) {
    try {
      const params = category ? { category } : {};
      const response = await api.get('/services/services', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get services');
    }
  }

  async getService(id) {
    try {
      const response = await api.get(`/services/services/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get service');
    }
  }

  async createService(serviceData) {
    try {
      const response = await api.post('/services/services', serviceData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create service');
    }
  }

  async updateService(id, serviceData) {
    try {
      const response = await api.put(`/services/services/${id}`, serviceData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update service');
    }
  }

  // Parts
  async getParts(category = null, lowStock = false) {
    try {
      const params = {};
      if (category) params.category = category;
      if (lowStock) params.low_stock = 'true';
      
      const response = await api.get('/services/parts', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get parts');
    }
  }

  async getPart(id) {
    try {
      const response = await api.get(`/services/parts/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get part');
    }
  }

  async createPart(partData) {
    try {
      const response = await api.post('/services/parts', partData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create part');
    }
  }

  async updatePart(id, partData) {
    try {
      const response = await api.put(`/services/parts/${id}`, partData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update part');
    }
  }

  async updatePartStock(id, quantity) {
    try {
      const response = await api.put(`/services/parts/${id}/stock`, { quantity });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update part stock');
    }
  }

  // Service Records
  async getServiceRecords() {
    try {
      const response = await api.get('/services/service-records');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get service records');
    }
  }

  async getServiceRecord(id) {
    try {
      const response = await api.get(`/services/service-records/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get service record');
    }
  }

  async createServiceRecord(recordData) {
    try {
      const response = await api.post('/services/service-records', recordData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create service record');
    }
  }

  async updateServiceRecord(id, recordData) {
    try {
      const response = await api.put(`/services/service-records/${id}`, recordData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update service record');
    }
  }

  async completeServiceRecord(id, completionData) {
    try {
      const response = await api.put(`/services/service-records/${id}/complete`, completionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to complete service record');
    }
  }
}

export const serviceService = new ServiceService();