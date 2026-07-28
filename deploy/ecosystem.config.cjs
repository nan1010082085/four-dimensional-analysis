module.exports = {
  apps: [{
    name: 'four-dimensional-analysis',
    script: 'app.py',
    interpreter: 'venv/bin/python',
    cwd: '/home/ubuntu/four-dimensional-analysis',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      PYTHONUNBUFFERED: '1'
    },
    error_file: 'logs/error.log',
    out_file: 'logs/output.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};
