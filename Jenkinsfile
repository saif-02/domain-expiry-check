pipeline {
    agent any
    
    stages {
        stage('Setup Environment') {
            steps {
                echo 'Setting up environment...'

                // Check GLIBC version and update if necessary
                sh '''
                echo "Checking GLIBC version..."
                GLIBC_VERSION=$(ldd --version | head -n 1 | awk '{print $NF}')
                REQUIRED_VERSION="2.28"

                if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$GLIBC_VERSION" | sort -V | head -n 1)" != "$REQUIRED_VERSION" ]; then
                    echo "Updating GLIBC to version $REQUIRED_VERSION..."
                    wget http://ftp.gnu.org/gnu/libc/glibc-2.28.tar.gz
                    tar -xvzf glibc-2.28.tar.gz
                    cd glibc-2.28
                    mkdir build
                    cd build
                    ../configure --prefix=/opt/glibc-2.28
                    make -j$(nproc)
                    sudo make install
                    export LD_LIBRARY_PATH=/opt/glibc-2.28/lib:$LD_LIBRARY_PATH
                else
                    echo "GLIBC version is sufficient: $GLIBC_VERSION"
                fi
                '''
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
