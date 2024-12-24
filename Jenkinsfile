pipeline {
    agent any
    
    stages {
        stage('Setup GLIBC') {
            steps {
                echo 'Setting up GLIBC...'
                sh '''
                # Define GLIBC version and paths
                REQUIRED_VERSION="2.28"
                INSTALL_DIR="/opt/glibc-${REQUIRED_VERSION}"

                # Check current GLIBC version
                CURRENT_VERSION=$(ldd --version | head -n 1 | awk '{print $NF}')
                echo "Current GLIBC version: $CURRENT_VERSION"

                if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$CURRENT_VERSION" | sort -V | head -n 1)" != "$REQUIRED_VERSION" ]; then
                    echo "Updating GLIBC to version $REQUIRED_VERSION..."
                    wget http://ftp.gnu.org/gnu/libc/glibc-${REQUIRED_VERSION}.tar.gz
                    tar -xvzf glibc-${REQUIRED_VERSION}.tar.gz
                    cd glibc-${REQUIRED_VERSION}
                    mkdir build && cd build
                    ../configure --prefix=${INSTALL_DIR}
                    make -j$(nproc)
                    make install
                    export LD_LIBRARY_PATH=${INSTALL_DIR}/lib:$LD_LIBRARY_PATH
                    echo "GLIBC updated successfully."
                else
                    echo "GLIBC is already up-to-date."
                fi
                '''
            }
        }
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
