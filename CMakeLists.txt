cmake_minimum_required(VERSION 3.10)
project(affordance_based_explanations)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# The service of the QSR server: an angle in, a spatial relation out.
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/QSRService.srv"
)

# The nodes and the modules they import are installed side by side, since a
# Python script finds the modules that lie in its own directory.
install(PROGRAMS
  scripts/aff.py
  scripts/planner.py
  scripts/qsr.py
  scripts/verbalize.py
  scripts/visualize.py
  scripts/explanation_node.py
  scripts/qsr_server.py
  scripts/qsr_client.py
  scripts/tts_tiago.py
  scripts/gtts_run.py
  scripts/polly_run.py
  scripts/pyttsx3/ttss.py
  scripts/pyttsx3/ttsc.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch ontologies maps worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
