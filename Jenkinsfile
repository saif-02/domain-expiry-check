pipeline {
    agent any
    
    stages {
        stage('Run Python Script') {
            steps {
                script {
                    // Run the Python script and capture its output
                    def pythonOutput = sh(
                        script: 'python3 your_script.py',
                        returnStdout: true
                    ).trim()
                    
                    // Save the output for use in the post block
                    writeFile file: 'python_output.txt', text: pythonOutput
                }
            }
        }
    }
    
    post {
        always {
            script {
                // Read the Python script output
                def pythonReportDetails = readFile('python_output.txt')
                
                // Send email
                emailext(
                    subject: "Build ${env.BUILD_NUMBER} - Python Script Report",
                    body: """
                    Hello Team,
                    
                    The latest build ${env.BUILD_NUMBER} has completed. Here are the details from the Python script:
                    
                    ${pythonReportDetails}
                    
                    Regards,
                    Jenkins
                    """,
                    to: 'team@example.com'
                )
            }
        }
    }
}
