program test_pdf_node
  implicit none
  double precision x, q, pdf(-6:7)
  call NNPDFDriver('NNPDF23_lo_as_0130_qed_mem0.grid')
  call NNinitPDF(0)
  x = 0.1d0
  q = sqrt(8286.427728546843d0)
  call NNevolvePDF(x,q,pdf)
  write(*,*) q, pdf(0), pdf(2), pdf(-2), pdf(1), pdf(-1)
end
